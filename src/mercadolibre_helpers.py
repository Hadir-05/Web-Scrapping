"""
Fonctions helper pour le traitement d'images avec CLIP, CLIPSeg, U-Net
Pour l'intégration MercadoLibre
"""

import pillow_avif
from PIL import Image
import requests
import torch
from typing import Tuple, Optional, Union
from skimage.morphology import remove_small_objects
import numpy as np
from scipy import ndimage
from torchvision import transforms
import cv2
import segmentation_models_pytorch as smp
import os
import json
from tqdm import tqdm
from collections import defaultdict
from numpy.linalg import norm
import timm
import shutil


# =====================================================
# 2. Chargement des images
# =====================================================
def load_image(path_or_url):
    if path_or_url.startswith("http"):
        image = Image.open(requests.get(path_or_url, stream=True).raw).convert("RGB")
    else:
        image = Image.open(path_or_url).convert("RGB")
    return image

def load_vit_model_chanelcategories(model_path="vit_base_patch16_224_best.pth", num_classes=14, device="cpu"):
    model = timm.create_model("vit_base_patch16_224", pretrained=False, num_classes=num_classes)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    model.to(device)
    return model

def verify_image_category(model, image, user_choice, device):
    """
    Prédit la catégorie d'une image et vérifie si elle correspond
    au produit choisi par l'utilisateur.
    """
    label_names = [
        "Bags",
        "Buttons",
        "Accessories",
        "Clothes",
        "Costume Jewelry",
        "Electronic Device Covers",
        "Eyewear",
        "Shoes",
        "Small Leather Goods",
        "Coco Crush",
        "N5",
        "Other Fine Jewelry",
        "Perfumes",
        "Watches"
    ]

    user_to_model_map = {
        # Bags
        "255": "Bags",
        "Timeless": "Bags",
        "Chanel 22": "Bags",

        # Shoes
        "Slingback": "Shoes",
        "Baskets": "Shoes",

        # Watches
        "J12": "Watches",
        "Première": "Watches",

        # Jewelry & fashion
        "Coco Crush": "Coco Crush",
        "Costume Jewelry": "Costume Jewelry",
        "Veste Tweed": "Clothes",
        "Accessories": "Accessories",

        # Perfumes
        "Coco Mademoiselle": "Perfumes"
    }


    # Charger l'image si c'est un chemin
    if isinstance(image, str):
        image = load_image(image)

    # Transformations identiques à celles du modèle
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])
    img_tensor = transform(image).unsqueeze(0).to(device)

    # Prédiction
    with torch.no_grad():
        outputs = model(img_tensor)
        _, pred = torch.max(outputs, 1)
        predicted_label = label_names[pred.item()]

    if predicted_label == 'Small Leather Goods':
        predicted_label = 'Bags'
    # Récupérer la catégorie attendue pour le choix utilisateur
    expected_label = user_to_model_map.get(user_choice)

    # Vérification
    is_match = (predicted_label == expected_label)

    return {
        "predicted_label": predicted_label,
        "expected_label": expected_label,
        "is_match": is_match
    }



def get_crop_clip_seg(
    pil_image: Image.Image,
    prompt: str,
    clipseg_model,
    clipseg_processor,
    device: Union[str, torch.device] = "cpu",
    threshold: float = 0.4,
    min_size: int = 50,
    margin: float = 0.05,
    bg_color: Union[int, Tuple[int,int,int]] = 127,
    resize_mask_mode: str = "bilinear",
    debug: bool = False
) -> Optional[Tuple[Image.Image, tuple, np.ndarray]]:
    """
    Compute a mask with CLIPSeg, clean it, overlay on the image with neutral background,
    crop around the mask with a margin and return the cropped image (and bbox, bin_mask).

    Args:
        pil_image: PIL.Image RGB
        prompt: prompt text for CLIPSeg
        clipseg_model: CLIPSegForImageSegmentation instance
        clipseg_processor: CLIPSegProcessor instance
        device: "cpu" or "cuda"
        threshold: threshold to binarize the sigmoid mask (0-1)
        min_size: minimum connected component size to keep (pixels)
        margin: relative margin added around bbox (fraction of bbox size)
        bg_color: neutral background color (int or (r,g,b))
        resize_mask_mode: "bilinear" or "nearest" for resizing mask to image size
        debug: if True returns intermediate visuals via prints (no plotting)

    Returns:
        (cropped_pil_image, bbox (x1,y1,x2,y2), mask_bin) or None if no region found.
    """
    # --- 1. Prepare and run CLIPSeg ---
    clipseg_model.to(device)
    inputs = clipseg_processor(text=[prompt], images=[pil_image], return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = clipseg_model(**inputs)
    logits = outputs.logits.squeeze().cpu().numpy()  # shape e.g. (H', W') or (H, W)
    prob = 1.0 / (1.0 + np.exp(-logits))  # sigmoid

    # --- 2. Resize mask to input image size (keep float 0-1) ---
    img_w, img_h = pil_image.size
    # convert to 0-255 uint8 then back to float like in ton code for stable resizing
    prob_u8 = (prob * 255.0).astype(np.uint8)
    mask_pil = Image.fromarray(prob_u8)
    resample = Image.BILINEAR if resize_mask_mode == "bilinear" else Image.NEAREST
    mask_resized = mask_pil.resize((img_w, img_h), resample=resample)
    mask = np.array(mask_resized).astype(np.float32) / 255.0  # float 0..1

    # --- 3. Threshold & clean small objects & fill holes ---
    mask_bin = (mask > threshold).astype(np.uint8)

    # remove very small objects (requires bool array)
    mask_bool = mask_bin.astype(bool)
    if mask_bool.sum() == 0:
        if debug:
            print("[get_crop_clip_seg] Aucun pixel après seuillage.")
        return None

    mask_bool = remove_small_objects(mask_bool, min_size=min_size)
    mask_bool = ndimage.binary_fill_holes(mask_bool).astype(np.uint8)

    if mask_bool.sum() == 0:
        if debug:
            print("[get_crop_clip_seg] Aucun composant suffisamment grand après filtrage.")
        return None

    # --- 4. Compute bbox of remaining mask ---
    ys, xs = np.where(mask_bool > 0)
    if len(xs) == 0 or len(ys) == 0:
        if debug:
            print("[get_crop_clip_seg] Pas de région détectée.")
        return None

    x1, x2 = int(xs.min()), int(xs.max())
    y1, y2 = int(ys.min()), int(ys.max())

    # add margin in pixels
    box_w = x2 - x1 + 1
    box_h = y2 - y1 + 1
    pad_x = int(box_w * margin)
    pad_y = int(box_h * margin)
    x1m = max(0, x1 - pad_x)
    y1m = max(0, y1 - pad_y)
    x2m = min(img_w, x2 + pad_x)
    y2m = min(img_h, y2 + pad_y)
    bbox = (x1m, y1m, x2m, y2m)

    # --- 5. Create image with neutral background where mask is 0 ---
    img_np = np.array(pil_image).astype(np.uint8)  # H x W x 3
    if isinstance(bg_color, int):
        bg_arr = np.ones_like(img_np, dtype=np.uint8) * bg_color
    else:
        # RGB tuple
        bg_arr = np.ones_like(img_np, dtype=np.uint8)
        bg_arr[..., 0] = bg_color[0]
        bg_arr[..., 1] = bg_color[1]
        bg_arr[..., 2] = bg_color[2]

    mask_3ch = np.stack([mask_bool]*3, axis=-1).astype(np.uint8)
    composed = np.where(mask_3ch == 1, img_np, bg_arr)

    # --- 6. Crop the composed image with bbox ---
    cropped = composed[y1m:y2m, x1m:x2m]
    cropped_pil = Image.fromarray(cropped)

    # Optionally return also the full-size mask_bin for later use
    if debug:
        print(f"[get_crop_clip_seg] bbox={bbox}, mask_area={mask_bool.sum()} px")

    return cropped_pil, bbox, mask_bool


def get_clip_embedding(img, clip_model, clip_processor, device="cuda"):
    inputs = clip_processor(images=img, return_tensors="pt").to(device)
    with torch.no_grad():
        emb = clip_model.get_image_features(**inputs)
    emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb.cpu()

def compute_patch_params(mask, ratio=1/6):
    mask_bin = (mask > 0.4).astype(np.uint8)
    sac_area = np.sum(mask_bin)
    fermoir_area = sac_area * ratio
    patch_size = int(np.sqrt(fermoir_area))
    stride = patch_size // 2
    return patch_size, stride

def get_transforms(img_size=224):
    return transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                                [0.229, 0.224, 0.225])
    ])

def load_unet(model_path, device='cpu'):
    model = smp.Unet(encoder_name="resnet34", encoder_weights=None,
                     in_channels=3, classes=1)
    model.load_state_dict(torch.load(model_path, map_location=device))
    return model.to(device).eval()


def get_crop_fermoir(
    cand_image: Image.Image,
    mask_sac: np.ndarray,
    clipseg_model,
    clipseg_processor,
    get_crop_clip_seg_fn,
    unet_model=None,
    clip_model=None,
    clip_processor=None,
    fermoir_db_embs=None,
    device="cuda",
    prompts=None,
    methods=("idea1", "idea2", "idea3"),
    ratios=(1/3, 1/4, 1/5, 1/6, 1/7),
    threshold=0.2,
    min_size=50,
    margin=0.05,
    bg_color=(127,127,127),
    debug=False
):
    """
    Combine 3 méthodes de détection du fermoir :
    - idée1 : CLIPSeg nested segmentation multi-prompts (sac -> fermoir)
    - idée2 : UNet fermoir segmentation
    - idée3 : Patch search CLIP embeddings

    Retour : liste de crops PIL (ou None si rien trouvé)
    """

    crops = []

    # ---------- IDÉE 1 : CLIPSeg nested segmentation MULTI-PROMPTS ----------

    # ---------- IDÉE 1 : CLIPSeg nested segmentation MULTI-PROMPTS ----------
    if "idea1" in methods and prompts is not None:
        if debug:
            print("\n🧠 [Idée 1] CLIPSeg multi-prompts : sac puis fermoir")

        for i, sac_prompt in enumerate(prompts["sac"]):
            if debug:
                print(f"   👜 Prompt sac {i+1}/{len(prompts['sac'])}: '{sac_prompt}'")

            try:
                sac_crop, bbox_sac, _ = get_crop_clip_seg_fn(
                    pil_image=cand_image,
                    prompt=sac_prompt,
                    clipseg_model=clipseg_model,
                    clipseg_processor=clipseg_processor,
                    device=device,
                    threshold=threshold,
                    min_size=min_size,
                    margin=margin,
                    bg_color=bg_color,
                    debug=debug
                )
            except Exception as e:
                if debug:
                    print(f"   ⚠️ Erreur lors du crop sac : {e}")
                continue

            if sac_crop is None:
                if debug:
                    print("      ⚠️ Aucun sac détecté pour ce prompt.")
                continue

            # ---- boucle sur les prompts fermoir ----
            for j, fermoir_prompt in enumerate(prompts["fermoir"]):
                if debug:
                    print(f"      🔑 Prompt fermoir {j+1}/{len(prompts['fermoir'])}: '{fermoir_prompt}'")

                try:
                    result = get_crop_clip_seg_fn(
                        pil_image=sac_crop,
                        prompt=fermoir_prompt,
                        clipseg_model=clipseg_model,
                        clipseg_processor=clipseg_processor,
                        device=device,
                        threshold=threshold,
                        min_size=min_size,
                        margin=margin,
                        bg_color=bg_color,
                        debug=debug
                    )

                    if result is None:
                        if debug:
                            print("         ⚠️ Aucun fermoir détecté.")
                        continue

                    fermoir_crop, bbox_f, _ = result
                    crops.append(fermoir_crop)

                    if debug:
                        print("         ✅ Fermoir détecté.")

                except Exception as e:
                    if debug:
                        print(f"         ⚠️ Erreur sur prompt '{fermoir_prompt}': {e}")
                    continue

        if debug:
            print(f"   ✅ Total {len(crops)} crops trouvés avec CLIPSeg (multi-prompts).")


    # ---------- IDÉE 2 : UNet segmentation ----------
    if "idea2" in methods and unet_model is not None:
        try:
            if debug:
                print("\n🧠 [Idée 2] UNet segmentation du fermoir")



            # Préparation image
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406],
                                    [0.229, 0.224, 0.225])
            ])
            img_t = transform(cand_image).unsqueeze(0).to(device)

            # Prédiction
            with torch.no_grad():
                pred = unet_model(img_t)
                mask = torch.sigmoid(pred).squeeze().cpu().numpy()

            # Resize du masque à la taille originale de l'image
            mask = cv2.resize(mask, cand_image.size, interpolation=cv2.INTER_LINEAR)

            # Seuillage
            mask = (mask > threshold).astype(np.uint8)

            # Post-traitement morphologique
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
            mask = cv2.dilate(mask, kernel, iterations=2)
            mask = mask.astype(bool)
            mask = remove_small_objects(mask, min_size=100)
            mask = ndimage.binary_fill_holes(mask).astype(np.uint8)

            # Extraction du bounding box
            ys, xs = np.where(mask > 0)
            if len(xs) > 0 and len(ys) > 0:
                x1, x2, y1, y2 = xs.min(), xs.max(), ys.min(), ys.max()

                # Sécurité : clamp pour ne pas dépasser les bords
                W, H = cand_image.size
                x1, x2 = max(0, x1), min(W, x2)
                y1, y2 = max(0, y1), min(H, y2)

                fermoir_crop = cand_image.crop((x1, y1, x2, y2))
                crops.append(fermoir_crop)

                if debug:
                    print(f"   ✅ Fermoir détecté par UNet ({x1},{y1},{x2},{y2})")
            else:
                if debug:
                    print("   ⚠️ Aucun fermoir détecté par UNet (masque vide).")

        except Exception as e:
            if debug:
                print(f"[idée2] ❌ Erreur : {e}")


    # ---------- IDÉE 3 : Patch search CLIP embeddings ----------
    if "idea3" in methods and clip_model is not None and fermoir_db_embs is not None:
        try:
            if debug:
                print("\n🧠 [Idée 3] Patch search CLIP multi-ratios")

            W, H = cand_image.size
            best_crops = []

            for ratio in ratios:
                patch_size, stride = compute_patch_params(mask_sac, ratio)
                best_score, best_box = 0, None

                for y in range(0, H - patch_size, stride):
                    for x in range(0, W - patch_size, stride):
                        patch = cand_image.crop((x, y, x+patch_size, y+patch_size))
                        emb_patch = get_clip_embedding(patch, clip_model, clip_processor, device=device)
                        scores = [(emb_patch @ db_emb.T).item() for db_emb in fermoir_db_embs]
                        score = max(scores)
                        if score > best_score:
                            best_score = score
                            best_box = (x, y, x+patch_size, y+patch_size)

                if best_box:
                    crop = cand_image.crop(best_box)
                    best_crops.append(crop)

            if best_crops:
                crops.extend(best_crops)
                if debug:
                    print(f"   ✅ {len(best_crops)} crops CLIP patch trouvés.")

        except Exception as e:
            if debug:
                print("[idée3] ❌ Erreur :", e)

    # ---------- Validation finale ----------
    crops = [c for c in crops if c is not None]
    if len(crops) == 0:
        if debug:
            print("[get_crop_fermoir] ❌ Aucune région détectée.")
        return None
    else:
        if debug:
            print(f"[get_crop_fermoir] ✅ Total final : {len(crops)} crops valides.")
        return crops



# -----------------------
# Helpers I/O & util
# -----------------------
def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def save_embedding_bundle(path_npz, metadata_list):
    # metadata_list: list of dicts where each has 'embedding' key (np.array)
    embs = np.stack([m['embedding'] for m in metadata_list], axis=0)
    # remove the arrays from metadata for JSON-safe storage
    meta_copy = []
    for m in metadata_list:
        m2 = m.copy()
        del m2['embedding']
        meta_copy.append(m2)
    np.savez_compressed(path_npz, embeddings=embs, metadata=json.dumps(meta_copy))
    # alternatively, save embeddings .npy + metadata .json separately

def load_embedding_bundle(path_npz):
    d = np.load(path_npz, allow_pickle=True)
    embs = d['embeddings']
    meta = json.loads(str(d['metadata'].tolist()))
    # reattach embeddings into metadata dicts
    for i, m in enumerate(meta):
        m['embedding'] = embs[i]
    return meta

# -----------------------
# 1) Build reference database from a single reference image
# -----------------------



def build_reference_from_image(
    ref_image: Image.Image,
    product_name: str,
    PRODUCT_PROMPTS: dict,
    clipseg_model=None,
    clipseg_processor=None,
    get_crop_clip_seg_fn=None,
    get_crop_fermoir_fn=None,
    clip_model=None,
    clip_processor=None,
    fermoir_db_embs=None,
    unet_model=None,
    out_dir="reference_db",
    device="cuda",
    threshold=0.35,
    min_size=50,
    margin=0.05,
    bg_color=(127,127,127),
    debug=False
):
    """
    Calcule les embeddings de référence d'un produit à partir d'une seule image.
    Inclut des sécurités :
      - gestion d'erreurs locales
      - ajout d'un embedding global fallback pour chaque label
    """
    # Création / réinitialisation du dossier de sortie
    product_out_dir = os.path.join(out_dir, product_name.replace(" ", "_"))
    if os.path.exists(product_out_dir):
        shutil.rmtree(product_out_dir)
    os.makedirs(product_out_dir, exist_ok=True)

    ref_items = []
    prompts_for_product = PRODUCT_PROMPTS.get(product_name)
    if prompts_for_product is None:
        raise ValueError(f"Produit inconnu: {product_name}")

    if debug:
        print(f"\n[REF] ==== Traitement produit: {product_name} ====")

    # Pour chaque label (ex: sac, fermoir, chaîne, logo)
    for label, prompt_list in prompts_for_product.items():
        label_crops = []
        if debug:
            print(f"\n[REF] Label '{label}' ({len(prompt_list)} prompts)")

        for i, prompt in enumerate(prompt_list):
            try:
                res = get_crop_clip_seg_fn(
                    pil_image=ref_image,
                    prompt=prompt,
                    clipseg_model=clipseg_model,
                    clipseg_processor=clipseg_processor,
                    device=device,
                    threshold=threshold,
                    min_size=min_size,
                    margin=margin,
                    bg_color=bg_color,
                    debug=False
                )
                if res is None:
                    if debug:
                        print(f"  ⚠️  Aucun crop trouvé pour prompt '{prompt}'")
                    continue

                crop_img, bbox, mask = res
                fname = f"{product_name}_{label}_p{i+1}.png".replace(" ", "_")
                crop_path = os.path.join(product_out_dir, fname)
                crop_img.save(crop_path)

                emb = get_clip_embedding(crop_img, clip_model, clip_processor, device=device)
                emb = emb.cpu().numpy().reshape(-1)
                emb = emb / np.linalg.norm(emb)
                label_crops.append(emb)

                ref_items.append({
                    "source_img": None,
                    "product": product_name,
                    "label": label,
                    "prompt": prompt,
                    "bbox": bbox,
                    "crop_path": crop_path,
                    "embedding": emb
                })

            except Exception as e:
                if debug:
                    print(f"  ❌ Erreur sur prompt '{prompt}': {e}")
                continue

        # ⚙️ Fallback : si aucun crop, ajouter l'image globale
        if not label_crops:
            if debug:
                print(f"  ⚠️ Aucun crop trouvé pour '{label}', ajout fallback global.")
            try:
                emb = get_clip_embedding(ref_image, clip_model, clip_processor, device=device)
                emb = emb.cpu().numpy().reshape(-1)
                emb = emb / np.linalg.norm(emb)
                fname = f"{product_name}_{label}_fallback_full.png".replace(" ", "_")
                crop_path = os.path.join(product_out_dir, fname)
                ref_image.save(crop_path)
                ref_items.append({
                    "source_img": None,
                    "product": product_name,
                    "label": label,
                    "prompt": "global_fallback",
                    "bbox": None,
                    "crop_path": crop_path,
                    "embedding": emb
                })
            except Exception as e:
                if debug:
                    print(f"  ❌ Erreur fallback label '{label}': {e}")

    # 🔹 Gestion spéciale : fermoir pour Timeless / 255
    if product_name in {"Timeless", "255"}:
        if debug: print("\n[REF] Ajout des crops 'fermoir' via get_crop_fermoir...")
        try:
            fermoir_crops = get_crop_fermoir_fn(
                cand_image=ref_image,
                mask_sac=None,
                clipseg_model=clipseg_model,
                clipseg_processor=clipseg_processor,
                get_crop_clip_seg_fn=get_crop_clip_seg_fn,
                unet_model=unet_model,
                clip_model=clip_model,
                clip_processor=clip_processor,
                fermoir_db_embs=fermoir_db_embs,
                device=device,
                prompts=PRODUCT_PROMPTS.get(product_name),
                methods=("idea1","idea2","idea3"),
                ratios=(1/3,1/4,1/5,1/6,1/7),
                threshold=threshold,
                min_size=min_size,
                margin=margin,
                bg_color=bg_color,
                debug=debug
            )
            if fermoir_crops:
                for k, fc in enumerate(fermoir_crops):
                    if isinstance(fc, dict) and 'crop' in fc:
                        crop_img = fc['crop']
                    else:
                        crop_img = fc
                    fname = f"{product_name}_fermoir_extra_{k+1}.png".replace(" ", "_")
                    crop_path = os.path.join(product_out_dir, fname)
                    crop_img.save(crop_path)
                    emb = get_clip_embedding(crop_img, clip_model, clip_processor, device=device)
                    emb = emb.cpu().numpy().reshape(-1)
                    emb = emb / np.linalg.norm(emb)
                    ref_items.append({
                        "source_img": None,
                        "product": product_name,
                        "label": "fermoir",
                        "prompt": "extra_fermoir",
                        "bbox": None,
                        "crop_path": crop_path,
                        "embedding": emb
                    })
        except Exception as e:
            if debug:
                print(f"  ❌ Erreur fermoir spéciale: {e}")

    # Sauvegarde finale
    npz_path = os.path.join(product_out_dir, f"{product_name}_reference.npz")
    save_embedding_bundle(npz_path, ref_items)

    if debug:
        print(f"\n✅ [REF] {len(ref_items)} embeddings sauvegardés dans {npz_path}")

    return ref_items, npz_path




# -----------------------
# 2) Process a folder of candidate images (batch)
# -----------------------
def build_candidates_db_from_folder(
    folder_path: str,
    product_name: str,
    PRODUCT_PROMPTS: dict,
    clipseg_model=None,
    clipseg_processor=None,
    get_crop_clip_seg_fn=None,
    get_crop_fermoir_fn=None,
    clip_model=None,
    clip_processor=None,
    fermoir_db_embs=None,
    unet_model=None,
    model_chanelcategories=None,
    out_dir="candidates_db",
    device="cuda",
    threshold=0.35,
    min_size=50,
    margin=0.05,
    bg_color=(127,127,127),
    debug=False
):
    """
    Construit la base de candidats pour un produit à partir d'un dossier d'images.
    - Gère les erreurs sans bloquer le traitement.
    - Pour chaque label, ajoute un embedding global (image complète) en fallback.
    - Pour Timeless / Chanel 255, applique get_crop_fermoir.
    """

    # Créer / réinitialiser le dossier de sortie
    product_out_dir = os.path.join(out_dir, product_name.replace(" ", "_"))
    if os.path.exists(product_out_dir):
        shutil.rmtree(product_out_dir)
    os.makedirs(product_out_dir, exist_ok=True)

    all_meta = []
    product_prompts = PRODUCT_PROMPTS.get(product_name)
    if not product_prompts:
        raise ValueError(f"[CAND] Aucun prompt trouvé pour le produit '{product_name}'")

    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg','.jpeg','.png','.avif'))]

    for fname in tqdm(image_files, desc=f"Candidats {product_name}"):
        path_img = os.path.join(folder_path, fname)
        try:
            img = load_image(path_img)
        except Exception as e:
            if debug:
                print(f"[WARN] Impossible d'ouvrir {fname}: {e}")
            continue

        if debug:
            print(f"\n[CAND] ==== {fname} ====")

        match = verify_image_category(model_chanelcategories, img, user_choice=product_name, device=device)
        print(match["predicted_label"], match["expected_label"], match["is_match"])

        if match['is_match']:

            # -------- Crops par label --------
            for label, prompt_list in product_prompts.items():
                label_crops = []
                if debug:
                    print(f"[CAND] Label '{label}' ({len(prompt_list)} prompts)")

                for i, prompt in enumerate(prompt_list):
                    try:
                        res = get_crop_clip_seg_fn(
                            pil_image=img,
                            prompt=prompt,
                            clipseg_model=clipseg_model,
                            clipseg_processor=clipseg_processor,
                            device=device,
                            threshold=threshold,
                            min_size=min_size,
                            margin=margin,
                            bg_color=bg_color,
                            debug=False
                        )
                        if res is None:
                            if debug:
                                print(f"  ⚠️ Aucun crop pour prompt '{prompt}'")
                            continue

                        crop_img, bbox, mask = res
                        save_name = f"{os.path.splitext(fname)[0]}__{product_name}__{label}__p{i+1}.png".replace(" ", "_")
                        save_path = os.path.join(product_out_dir, save_name)
                        crop_img.save(save_path)

                        emb = get_clip_embedding(crop_img, clip_model, clip_processor, device=device)
                        emb = emb.cpu().numpy().reshape(-1)
                        emb = emb / np.linalg.norm(emb)

                        all_meta.append({
                            "source_img": path_img,
                            "product": product_name,
                            "label": label,
                            "prompt": prompt,
                            "bbox": bbox,
                            "crop_path": save_path,
                            "embedding": emb
                        })
                        label_crops.append(emb)

                    except Exception as e:
                        if debug:
                            print(f"  ❌ Erreur sur prompt '{prompt}': {e}")
                        continue

                # ⚙️ Fallback global : ajouter l'image entière si aucun crop
                if not label_crops:
                    if debug:
                        print(f"  ⚠️ Aucun crop trouvé pour '{label}', ajout fallback global.")
                    try:
                        emb = get_clip_embedding(img, clip_model, clip_processor, device=device)
                        emb = emb.cpu().numpy().reshape(-1)
                        emb = emb / np.linalg.norm(emb)
                        save_name = f"{os.path.splitext(fname)[0]}__{product_name}__{label}__fallback_full.png".replace(" ", "_")
                        save_path = os.path.join(product_out_dir, save_name)
                        img.save(save_path)
                        all_meta.append({
                            "source_img": path_img,
                            "product": product_name,
                            "label": label,
                            "prompt": "global_fallback",
                            "bbox": None,
                            "crop_path": save_path,
                            "embedding": emb
                        })
                    except Exception as e:
                        if debug:
                            print(f"  ❌ Erreur fallback '{label}' sur {fname}: {e}")

            # -------- Cas spécial fermoir --------
            if product_name in {"Timeless", "255"} and get_crop_fermoir_fn is not None:
                if debug:
                    print("[CAND] Traitement spécial 'fermoir'...")
                try:
                    fer_res = get_crop_fermoir_fn(
                        cand_image=img,
                        mask_sac=None,
                        clipseg_model=clipseg_model,
                        clipseg_processor=clipseg_processor,
                        get_crop_clip_seg_fn=get_crop_clip_seg_fn,
                        unet_model=unet_model,
                        clip_model=clip_model,
                        clip_processor=clip_processor,
                        fermoir_db_embs=fermoir_db_embs,
                        prompts=PRODUCT_PROMPTS[product_name],
                        methods=("idea1","idea2","idea3"),
                        device=device,
                        threshold=threshold,
                        min_size=min_size,
                        margin=margin,
                        bg_color=bg_color,
                        debug=debug
                    )
                    if fer_res:
                        for k, fc in enumerate(fer_res):
                            crop_img = fc if isinstance(fc, Image.Image) else fc.get("crop", None)
                            if crop_img is None:
                                continue

                            save_name = f"{os.path.splitext(fname)[0]}__{product_name}__fermoir_extra_{k+1}.png".replace(" ", "_")
                            save_path = os.path.join(product_out_dir, save_name)
                            crop_img.save(save_path)

                            emb = get_clip_embedding(crop_img, clip_model, clip_processor, device=device)
                            emb = emb.cpu().numpy().reshape(-1)
                            emb = emb / np.linalg.norm(emb)

                            all_meta.append({
                                "source_img": path_img,
                                "product": product_name,
                                "label": "fermoir",
                                "prompt": "extra_fermoir",
                                "bbox": None,
                                "crop_path": save_path,
                                "embedding": emb
                            })
                except Exception as e:
                    if debug:
                        print(f"  ❌ Erreur fermoir spéciale sur {fname}: {e}")

    # ---- Sauvegarde du bundle final ----
    npz_path = os.path.join(product_out_dir, f"{product_name}_candidates.npz")
    save_embedding_bundle(npz_path, all_meta)

    if debug:
        print(f"\n✅ [CAND] {len(all_meta)} embeddings enregistrés dans {npz_path}")

    return all_meta, npz_path

##########
def build_candidates_db_from_urls(
    listings: str,
    product_name: str,
    PRODUCT_PROMPTS: dict,
    clipseg_model=None,
    clipseg_processor=None,
    get_crop_clip_seg_fn=None,
    get_crop_fermoir_fn=None,
    clip_model=None,
    clip_processor=None,
    fermoir_db_embs=None,
    unet_model=None,
    model_chanelcategories=None,
    out_dir="candidates_db",
    device="cuda",
    threshold=0.35,
    min_size=50,
    margin=0.05,
    bg_color=(127,127,127),
    debug=False
):
    """
    Construit la base de candidats pour un produit à partir d'une liste de listings (URLs).
    - Gère les erreurs sans bloquer le traitement.
    - Pour chaque label, ajoute un embedding global (image complète) en fallback.
    - Pour Timeless / Chanel 255, applique get_crop_fermoir.
    """

    # Créer / réinitialiser le dossier de sortie
    product_out_dir = os.path.join(out_dir, product_name.replace(" ", "_"))
    if os.path.exists(product_out_dir):
        shutil.rmtree(product_out_dir)
    os.makedirs(product_out_dir, exist_ok=True)

    all_meta = []
    product_prompts = PRODUCT_PROMPTS.get(product_name)
    if not product_prompts:
        raise ValueError(f"[CAND] Aucun prompt trouvé pour le produit '{product_name}'")

    for ii, item in enumerate(listings):
        try:
            img = load_image(item["image_url"])
        except Exception as e:
            if debug:
                print(f"[WARN] Impossible d'ouvrir {item['image_url']}: {e}")
            continue

        if debug:
            print(f"\n[CAND] ==== {item['image_url']} ====")

        match = verify_image_category(model_chanelcategories, img, user_choice=product_name, device=device)
        print(match["predicted_label"], match["expected_label"], match["is_match"])

        if match['is_match']:

            # -------- Crops par label --------
            for label, prompt_list in product_prompts.items():
                label_crops = []
                if debug:
                    print(f"[CAND] Label '{label}' ({len(prompt_list)} prompts)")

                for i, prompt in enumerate(prompt_list):
                    try:
                        res = get_crop_clip_seg_fn(
                            pil_image=img,
                            prompt=prompt,
                            clipseg_model=clipseg_model,
                            clipseg_processor=clipseg_processor,
                            device=device,
                            threshold=threshold,
                            min_size=min_size,
                            margin=margin,
                            bg_color=bg_color,
                            debug=False
                        )
                        if res is None:
                            if debug:
                                print(f"  ⚠️ Aucun crop pour prompt '{prompt}'")
                            continue

                        crop_img, bbox, mask = res
                        save_name = f"{ii}__{product_name}__{label}__p{i+1}.png".replace(" ", "_")

                        save_path = os.path.join(product_out_dir, save_name)
                        crop_img.save(save_path)

                        emb = get_clip_embedding(crop_img, clip_model, clip_processor, device=device)
                        emb = emb.cpu().numpy().reshape(-1)
                        emb = emb / np.linalg.norm(emb)

                        all_meta.append({
                            "annonce_url": item["image_url"],
                            "source_img": item["listing_url"],
                            "product": product_name,
                            "label": label,
                            "prompt": prompt,
                            "bbox": bbox,
                            "crop_path": save_path,
                            "embedding": emb
                        })
                        label_crops.append(emb)

                    except Exception as e:
                        if debug:
                            print(f"  ❌ Erreur sur prompt '{prompt}': {e}")
                        continue

                # ⚙️ Fallback global : ajouter l'image entière si aucun crop
                if not label_crops:
                    if debug:
                        print(f"  ⚠️ Aucun crop trouvé pour '{label}', ajout fallback global.")
                    try:
                        emb = get_clip_embedding(img, clip_model, clip_processor, device=device)
                        emb = emb.cpu().numpy().reshape(-1)
                        emb = emb / np.linalg.norm(emb)
                        save_name = f"{ii}__{product_name}__{label}__fallback_full.png".replace(" ", "_")
                        save_path = os.path.join(product_out_dir, save_name)
                        img.save(save_path)
                        all_meta.append({
                            "annonce_url": item["image_url"],
                            "source_img": item["listing_url"],
                            "label": label,
                            "prompt": "global_fallback",
                            "bbox": None,
                            "crop_path": save_path,
                            "embedding": emb
                        })
                    except Exception as e:
                        if debug:
                            print(f"  ❌ Erreur fallback '{label}' sur {ii}: {e}")

            # -------- Cas spécial fermoir --------
            if product_name in {"Timeless", "255"} and get_crop_fermoir_fn is not None:
                if debug:
                    print("[CAND] Traitement spécial 'fermoir'...")
                try:
                    fer_res = get_crop_fermoir_fn(
                        cand_image=img,
                        mask_sac=None,
                        clipseg_model=clipseg_model,
                        clipseg_processor=clipseg_processor,
                        get_crop_clip_seg_fn=get_crop_clip_seg_fn,
                        unet_model=unet_model,
                        clip_model=clip_model,
                        clip_processor=clip_processor,
                        fermoir_db_embs=fermoir_db_embs,
                        prompts=PRODUCT_PROMPTS[product_name],
                        methods=("idea1","idea2","idea3"),
                        device=device,
                        threshold=threshold,
                        min_size=min_size,
                        margin=margin,
                        bg_color=bg_color,
                        debug=debug
                    )
                    if fer_res:
                        for k, fc in enumerate(fer_res):
                            crop_img = fc if isinstance(fc, Image.Image) else fc.get("crop", None)
                            if crop_img is None:
                                continue

                            save_name = f"{ii}__{product_name}__fermoir_extra_{k+1}.png".replace(" ", "_")
                            save_path = os.path.join(product_out_dir, save_name)
                            crop_img.save(save_path)

                            emb = get_clip_embedding(crop_img, clip_model, clip_processor, device=device)
                            emb = emb.cpu().numpy().reshape(-1)
                            emb = emb / np.linalg.norm(emb)

                            all_meta.append({
                                "annonce_url": item["image_url"],
                                "source_img": item["listing_url"],
                                "label": "fermoir",
                                "prompt": "extra_fermoir",
                                "bbox": None,
                                "crop_path": save_path,
                                "embedding": emb
                            })
                except Exception as e:
                    if debug:
                        print(f"  ❌ Erreur fermoir spéciale sur {ii}: {e}")

    # ---- Sauvegarde du bundle final ----
    npz_path = os.path.join(product_out_dir, f"{product_name}_candidates.npz")
    save_embedding_bundle(npz_path, all_meta)

    if debug:
        print(f"\n✅ [CAND] {len(all_meta)} embeddings enregistrés dans {npz_path}")

    return all_meta, npz_path





def group_embeddings_by_label(meta_list):
    grouped = defaultdict(lambda: {"labels": defaultdict(list), "annonce_url": None})

    for item in meta_list:
        src = item['source_img']
        grouped[src]["labels"][item['label']].append(item['embedding'])
        grouped[src]["annonce_url"] = item.get("annonce_url")

    return grouped



def cosine_similarity(a, b):
    if a is None or b is None:
        return 0.0
    return np.dot(a, b) / (norm(a) * norm(b) + 1e-8)

def compute_label_similarity(ref_embs, cand_embs, sim_threshold=0.3):
    """Compare les embeddings d'un label entre la référence et un candidat."""
    if len(ref_embs) == 0 or len(cand_embs) == 0:
        return 0.0

    sims = []
    for ref in ref_embs:
        # trouver la meilleure correspondance dans les embeddings candidats
        best_sim = max(cosine_similarity(ref, c) for c in cand_embs)
        if best_sim >= sim_threshold:
            sims.append(best_sim)

    if len(sims) == 0:
        return None
    return float(np.mean(sims))  # moyenne des meilleures similarités par ref


def compute_image_similarity(ref_dict, cand_dict, product_name=None, sim_threshold=0.3, PRODUCT_LABEL_WEIGHTS=None):
    """
    Compare tous les labels d'une image candidate à la référence.
    Utilise des poids spécifiques selon le produit si disponibles.
    """
    label_scores = {}
    all_labels = set(ref_dict.keys()) | set(cand_dict.keys())

    for label in all_labels:
        ref_embs = ref_dict.get(label, [])
        cand_embs = cand_dict.get(label, [])
        score = compute_label_similarity(ref_embs, cand_embs, sim_threshold)
        if score is None:
            continue
        label_scores[label] = score

    # ✅ Sélection automatique du dictionnaire de poids
    if product_name and product_name in PRODUCT_LABEL_WEIGHTS:
        label_weights = PRODUCT_LABEL_WEIGHTS[product_name]
        total_weight = sum(label_weights.get(lbl, 1.0) for lbl in label_scores)
        global_score = sum(label_scores[lbl] * label_weights.get(lbl, 1.0)
                           for lbl in label_scores) / total_weight
    else:
        # fallback : moyenne simple
        global_score = np.mean(list(label_scores.values())) if label_scores else 0.0

    return global_score, label_scores

def compare_candidates_to_reference(ref_meta, cand_meta, sim_threshold=0.3, product_name=None, PRODUCT_LABEL_WEIGHTS=None):
    ref_grouped = group_embeddings_by_label(ref_meta)
    cand_grouped = group_embeddings_by_label(cand_meta)

    ref_img = list(ref_grouped.keys())[0]  # on suppose une seule image de référence
    ref_embs = ref_grouped[ref_img]["labels"]

    results = []

    for cand_name, cand_data in cand_grouped.items():
        cand_embs = cand_data["labels"]
        annonce_url = cand_data["annonce_url"]

        global_score, label_scores = compute_image_similarity(
            ref_embs, cand_embs,
            product_name=product_name,
            sim_threshold=sim_threshold,
            PRODUCT_LABEL_WEIGHTS=PRODUCT_LABEL_WEIGHTS
        )

        results.append({
            "candidate": cand_name,
            "annonce_url": annonce_url,
            "global_score": global_score,
            "label_scores": label_scores
        })

    results = sorted(results, key=lambda x: x["global_score"], reverse=True)

    # 2. Éliminer les doublons d'annonce_url en gardant la meilleure occurrence
    unique_results = []
    seen = set()

    for r in results:
        if r["annonce_url"] not in seen:
            unique_results.append({
                "candidate": r["candidate"],
                "annonce_url": r["annonce_url"],
                "global_score": r["global_score"],
                "label_scores": r["label_scores"]
            })
            seen.add(r["annonce_url"])

    # 3. Le résultat final sans doublons
    return unique_results
