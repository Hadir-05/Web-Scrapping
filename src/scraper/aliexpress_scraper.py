"""
Module de scraping AliExpress avec recherche par image - VERSION PROFESSIONNELLE
Inspiré de code production avec fingerprinting, sessions et routing
"""
import asyncio
import os
import re
import random as rnd
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
from urllib.parse import urljoin, urlparse

from crawlee import (
    ConcurrencySettings,
    Request,
    SkippedReason,
    service_locator,
)
from crawlee.sessions import SessionPool
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
from crawlee.storages import Dataset, RequestQueue
from crawlee.fingerprint_suite import (
    DefaultFingerprintGenerator,
    HeaderGeneratorOptions,
    ScreenOptions,
)

from src.models.data_models import ImageMetadata, ProductData


# Configuration
HEADLESS = True
TEMPO_DELAY = 2.0  # Délai aléatoire pour simuler comportement humain


def url_noparams(url: str) -> str:
    """Retire les paramètres d'une URL"""
    return url.split('?')[0] if '?' in url else url


class AliExpressImageSearchScraper:
    """
    Scraper AliExpress professionnel avec:
    - Fingerprint generation pour éviter la détection
    - Session pool pour gérer les sessions
    - Dataset API pour stockage structuré
    - Router avec labels pour séparer ITEM et ITEM_IMG
    - Upload d'image natif AliExpress
    """

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)

        # Dataset name: only a-z, 0-9, and hyphen (not at start/end)
        self.attempt_id = f"aliexpress-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.image_counter = 0
        self.product_counter = 0  # Pour numéroter les dossiers produits
        self.product_image_counters = {}  # Compteur d'images par produit {product_num: count}
        self.target_results = 0

    async def search_by_image(
        self,
        image_path: str,
        category: str = "",
        max_results: int = 50,
        headless: bool = True
    ) -> Tuple[List[ImageMetadata], List[ProductData]]:
        """
        Recherche sur AliExpress par upload d'image

        Args:
            image_path: Chemin vers l'image à uploader
            category: Catégorie pour filtrer (optionnel)
            max_results: Nombre max de résultats
            headless: Mode headless du navigateur
        """
        self.target_results = max_results
        self.image_counter = 0

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Initialiser les datasets
        item_dataset = await Dataset.open(name=f"{self.attempt_id}-items")
        img_dataset = await Dataset.open(name=f"{self.attempt_id}-images")

        # Fingerprint generator - génère des empreintes de navigateur réalistes
        fingerprint_generator = DefaultFingerprintGenerator(
            header_options=HeaderGeneratorOptions(
                browsers=["chrome", "firefox", "edge"],
                operating_systems=["windows", "linux"],
                devices=["desktop"],
                locales=["en-US", "fr-FR"],
            ),
            screen_options=ScreenOptions(min_width=1024, max_width=1920),
        )

        # Configuration Crawlee personnalisée
        custom_config = service_locator.get_configuration()
        custom_config.available_memory_ratio = 0.5
        custom_config.purge_on_start = True

        # Request queue nommée
        request_queue = await RequestQueue.open(name=self.attempt_id)

        # Crawler avec configuration avancée
        crawler = PlaywrightCrawler(
            request_manager=request_queue,
            max_requests_per_crawl=max_results * 2,  # Items + images
            configuration=custom_config,
            headless=headless,
            browser_type="chromium",
            keep_alive=False,
            # Session pool pour gérer les sessions
            use_session_pool=True,
            session_pool=SessionPool(
                max_pool_size=10,
                create_session_settings={'max_usage_count': 3}
            ),
            # Fingerprint pour éviter détection
            fingerprint_generator=fingerprint_generator,
            # Concurrency settings pour performance optimale
            concurrency_settings=ConcurrencySettings(
                min_concurrency=2,
                desired_concurrency=4,
                max_concurrency=6,
                max_tasks_per_minute=20
            )
        )

        # ========================
        # HANDLER: Default (Page de recherche)
        # ========================
        @crawler.router.default_handler
        async def search_handler(context: PlaywrightCrawlingContext) -> None:
            """
            Upload l'image et attend les résultats de recherche AliExpress
            """
            context.log.info(f"🔍 Processing {context.request.url}")

            # Tempo delay pour simuler comportement humain
            await asyncio.sleep(1 + (rnd.random() * TEMPO_DELAY))

            page = context.page

            # Fermer popup publicitaire si présent
            try:
                await page.locator("img[class^=pop-close-btn]").click(timeout=2000)
                context.log.info("✅ Popup fermée")
            except:
                context.log.info("ℹ️ Pas de popup")

            # Cliquer sur "Search by image"
            context.log.info("📸 Clic sur recherche par image...")
            try:
                # Plusieurs sélecteurs possibles
                search_by_img_selectors = [
                    'img[alt*="search by image"]',
                    'img[alt*="image search"]',
                    'div[class*="search-by-image"]',
                    'button[class*="image-search"]',
                ]

                clicked = False
                for selector in search_by_img_selectors:
                    try:
                        await page.locator(selector).first.click(timeout=3000)
                        clicked = True
                        context.log.info(f"✅ Cliqué avec sélecteur: {selector}")
                        break
                    except:
                        continue

                if not clicked:
                    # Fallback: essayer avec texte
                    await page.get_by_alt_text("recherche par image").click(timeout=5000)

            except Exception as e:
                context.log.error(f"❌ Impossible de trouver le bouton de recherche par image: {e}")
                return

            # Upload de l'image
            context.log.info(f"📤 Upload de l'image: {image_path}")
            try:
                await page.locator("input[type=file]").set_input_files(image_path)
                context.log.info("✅ Image uploadée avec succès")
            except Exception as e:
                context.log.error(f"❌ Erreur upload image: {e}")
                return

            # Attendre la redirection vers les résultats
            context.log.info("⏳ Attente des résultats...")
            try:
                await page.wait_for_url(
                    "**/w/wholesale-*.html*",
                    timeout=30000
                )
                context.log.info(f"✅ Résultats chargés: {page.url}")
            except:
                context.log.warning("⚠️ URL pattern non détecté, on continue...")

            await asyncio.sleep(1 + (rnd.random() * TEMPO_DELAY))

            # Scroll infini pour charger les produits lazy-loaded
            context.log.info("📜 Infinite scroll...")
            await context.infinite_scroll()

            # Déterminer le nombre de pages
            context.log.info("📄 Détection du nombre de pages...")
            max_pages = 1
            try:
                pagination_texts = await page.locator(
                    "div[class*=pagination]"
                ).all_text_contents()

                if pagination_texts:
                    for text in pagination_texts:
                        matches = re.findall(r'\d+', text)
                        if matches:
                            max_pages = max([int(m) for m in matches])
                            break

                context.log.info(f"📄 Nombre de pages détecté: {max_pages}")
            except Exception as e:
                context.log.warning(f"⚠️ Pagination non détectée: {e}")

            # Limiter à 10 pages max
            max_pages = min(max_pages, 10)

            # Extraire les produits de la page 1
            await self._extract_search_results(context, item_dataset, request_queue)

            # Ajouter les pages suivantes
            current_url = page.url
            base_url = url_noparams(current_url)

            for page_num in range(2, max_pages + 1):
                if '?' in current_url:
                    next_url = f"{base_url}?page={page_num}"
                else:
                    next_url = f"{base_url}&page={page_num}"

                context.log.info(f"📑 Ajout page {page_num}: {next_url}")
                await context.add_requests([
                    Request.from_url(next_url, label="SEARCH_PAGE")
                ])

        # ========================
        # HANDLER: Pages de recherche suivantes
        # ========================
        @crawler.router.handler("SEARCH_PAGE")
        async def search_page_handler(context: PlaywrightCrawlingContext) -> None:
            """Traite les pages de résultats suivantes"""
            context.log.info(f"📄 Page de recherche: {context.request.url}")

            await asyncio.sleep(1 + (rnd.random() * TEMPO_DELAY))
            await context.infinite_scroll()

            await self._extract_search_results(context, item_dataset, request_queue)

        # ========================
        # HANDLER: Page produit (ITEM)
        # ========================
        @crawler.router.handler("ITEM")
        async def item_handler(context: PlaywrightCrawlingContext) -> None:
            """Traite une page produit individuelle"""
            if context.response.status in [404, 403]:
                context.log.warning(f"⚠️ Page inaccessible: {context.response.status}")
                await context.page.close()
                return

            context.log.info(f"🛍️ Traitement produit: {context.request.url}")
            page = context.page
            item_url = url_noparams(context.request.url)

            await asyncio.sleep(1 + (rnd.random() * TEMPO_DELAY))

            # Incrémenter le compteur de produit
            self.product_counter += 1
            current_product_num = self.product_counter

            # Extraire les données
            try:
                # Titre
                title = await page.title()
                context.log.info(f"   📝 Titre: {title[:50]}...")

                # Prix - Stratégie ultra-robuste
                # Attendre que la page charge complètement
                await page.wait_for_load_state('domcontentloaded', timeout=15000)
                await asyncio.sleep(2)

                context.log.info("   💰 Recherche du prix avec stratégie ultra-robuste...")
                price = "N/A"

                # STRATÉGIE 1: Utiliser JavaScript pour chercher n'importe quel élément avec €,$,£,¥
                context.log.info("      Stratégie 1: JavaScript search pour symboles monétaires...")
                try:
                    price_js = await page.evaluate("""() => {
                        // Chercher tous les éléments contenant des symboles monétaires
                        const symbols = ['€', '$', '£', '¥', 'USD', 'EUR'];
                        const allElements = document.querySelectorAll('span, div, p');

                        for (let el of allElements) {
                            const text = el.textContent || '';
                            // Vérifier si contient un symbole et un nombre
                            if (symbols.some(s => text.includes(s)) && /\d/.test(text)) {
                                // Vérifier que c'est probablement un prix (pas trop long)
                                if (text.trim().length < 30 && text.trim().length > 1) {
                                    // Priorité aux éléments avec 'price' dans la classe
                                    const className = el.className || '';
                                    if (className.toLowerCase().includes('price')) {
                                        return text.trim();
                                    }
                                }
                            }
                        }

                        // Fallback: premier élément avec symbole monétaire et nombre
                        for (let el of allElements) {
                            const text = el.textContent || '';
                            if (symbols.some(s => text.includes(s)) && /\d/.test(text)) {
                                if (text.trim().length < 30 && text.trim().length > 1) {
                                    return text.trim();
                                }
                            }
                        }

                        return null;
                    }""")

                    if price_js:
                        price = price_js
                        context.log.info(f"   ✅ Prix trouvé avec JavaScript: {price}")
                except Exception as e:
                    context.log.info(f"      JavaScript search échoué: {e}")

                # STRATÉGIE 2: Si JavaScript n'a pas marché, essayer les sélecteurs CSS
                if price == "N/A":
                    context.log.info("      Stratégie 2: Sélecteurs CSS classiques...")
                    price_selectors = [
                        "span[class*='price-default']",
                        "span[class*='price--current']",
                        "span[class*='price--']",
                        "div[class*='price'] span",
                        "span[class*='Price']",
                        ".product-price",
                        "[data-spm-anchor-id*='price']",
                    ]

                    for idx, selector in enumerate(price_selectors):
                        try:
                            price_elem = await page.locator(selector).first.text_content(timeout=2000)
                            if price_elem and price_elem.strip() and len(price_elem.strip()) < 30:
                                price = price_elem.strip()
                                context.log.info(f"   ✅ Prix trouvé avec CSS #{idx+1} ({selector}): {price}")
                                break
                        except:
                            continue

                # STRATÉGIE 3: Regex sur tout le contenu visible de la page
                if price == "N/A":
                    context.log.info("      Stratégie 3: Regex sur contenu de page...")
                    try:
                        body_text = await page.locator('body').text_content(timeout=3000)
                        import re
                        # Pattern pour prix: nombre + symbole ou symbole + nombre
                        patterns = [
                            r'([0-9]+[,\.][0-9]{2}\s*€)',
                            r'(€\s*[0-9]+[,\.][0-9]{2})',
                            r'([0-9]+[,\.][0-9]{2}\s*\$)',
                            r'(\$\s*[0-9]+[,\.][0-9]{2})',
                        ]
                        for pattern in patterns:
                            matches = re.findall(pattern, body_text)
                            if matches:
                                price = matches[0]
                                context.log.info(f"   ✅ Prix trouvé avec regex: {price}")
                                break
                    except Exception as e:
                        context.log.info(f"      Regex search échoué: {e}")

                if price == "N/A":
                    context.log.warning("   ⚠️ Prix non trouvé avec toutes les stratégies")

                # Images produit - APPROCHE ULTRA-AGRESSIVE: Prendre TOUTES les grandes images
                context.log.info("   🖼️ Extraction des images (mode agressif)...")
                img_links = []

                # STRATÉGIE UNIQUE: JavaScript pour prendre TOUTES les images > 200px
                context.log.info("      JavaScript: Récupération de TOUTES les grandes images...")
                try:
                    imgs_js = await page.evaluate("""() => {
                        const images = [];
                        const allImgs = document.querySelectorAll('img');

                        console.log('Total images sur la page:', allImgs.length);

                        for (let img of allImgs) {
                            const src = img.src || img.getAttribute('src') || img.getAttribute('data-src');

                            if (src && src.includes('alicdn')) {
                                const width = img.naturalWidth || img.width || 0;
                                const height = img.naturalHeight || img.height || 0;

                                console.log('Image:', {
                                    src: src.substring(0, 80),
                                    width: width,
                                    height: height
                                });

                                // Prendre si > 200px dans au moins une dimension
                                if (width >= 200 || height >= 200) {
                                    // Améliorer la qualité
                                    let srcClean = src.replace('_50x50', '').replace('_100x100', '').replace('_150x150', '');
                                    srcClean = srcClean.replace('.webp', '.jpg');

                                    images.push({
                                        url: srcClean,
                                        width: width,
                                        height: height
                                    });
                                }
                            }
                        }

                        console.log('Images sélectionnées:', images.length);
                        return images;
                    }""")

                    context.log.info(f"         JavaScript a trouvé {len(imgs_js) if imgs_js else 0} grandes images")

                    if imgs_js and len(imgs_js) > 0:
                        # Prendre TOUTES les images (pas de limite à 3)
                        for idx, img_info in enumerate(imgs_js, 1):
                            url = img_info['url']
                            width = img_info['width']
                            height = img_info['height']

                            img_links.append(url)
                            context.log.info(f"         {idx}. {url[:70]}... ({width}x{height}px)")

                        context.log.info(f"      ✅ {len(img_links)} images récupérées")
                    else:
                        context.log.warning(f"      ⚠️ JavaScript n'a trouvé AUCUNE grande image!")

                except Exception as e:
                    context.log.error(f"      ❌ JavaScript échoué: {e}")
                    import traceback
                    context.log.error(f"      {traceback.format_exc()}")

                # FALLBACK: Si JavaScript a échoué, essayer méthode classique
                if len(img_links) == 0:
                    context.log.info("      FALLBACK: Méthode Playwright classique...")
                    try:
                        all_imgs = await page.locator("img").all()
                        context.log.info(f"         Playwright a trouvé {len(all_imgs)} images au total")

                        for idx, img in enumerate(all_imgs[:20], 1):  # Limiter à 20 premières
                            try:
                                src = await img.get_attribute("src")
                                if not src:
                                    src = await img.get_attribute("data-src")

                                if src and 'alicdn' in src:
                                    context.log.info(f"         {idx}. {src[:70]}...")
                                    img_links.append(src)

                            except Exception as e:
                                context.log.info(f"         Erreur image {idx}: {e}")

                        context.log.info(f"      Playwright: {len(img_links)} images récupérées")

                    except Exception as e:
                        context.log.error(f"      ❌ Fallback Playwright échoué: {e}")

                context.log.info(f"   📊 TOTAL FINAL: {len(img_links)} images à télécharger")

                # Ajouter les requêtes d'images (PRIORITÉ) avec le numéro de produit
                if len(img_links) > 0:
                    context.log.info(f"   📤 Ajout de {len(img_links)} images à la queue de téléchargement...")
                    for idx, img_url in enumerate(img_links):
                        context.log.info(f"      Ajout image {idx+1}/{len(img_links)}: {img_url[:60]}...")
                        await request_queue.add_requests([
                            Request.from_url(
                                url=img_url,
                                label="ITEM_IMG",
                                user_data={
                                    "product_url": item_url,
                                    "product_num": current_product_num  # Passer le numéro de produit
                                }
                            )
                        ], forefront=True)  # Priorité aux images
                        context.log.info(f"      ✅ Image {idx+1} ajoutée à la queue")
                    context.log.info(f"   ✅ Toutes les images ajoutées à la queue")
                else:
                    context.log.warning(f"   ⚠️ Aucune image à télécharger pour ce produit!")

                # Sauvegarder les données du produit
                item_data = {
                    "item_url": item_url,
                    "src_image": image_path,
                    "title": title,
                    "description": title,  # Description = titre pour l'instant
                    "collection_date": datetime.now().isoformat(),
                    "price": price,
                    "screenshot_path": "",
                    "product_image_paths": img_links,
                }

                await item_dataset.push_data(item_data)
                context.log.info(f"   ✅ Produit sauvegardé")

            except Exception as e:
                context.log.error(f"   ❌ Erreur extraction produit: {e}")

            await context.page.close()

        # ========================
        # HANDLER: Image produit (ITEM_IMG)
        # ========================
        @crawler.router.handler("ITEM_IMG")
        async def item_img_handler(context: PlaywrightCrawlingContext) -> None:
            """
            Télécharge une image de produit dans son sous-dossier.
            Version agressive: accepte TOUTES les images, logging détaillé.
            """
            img_url = context.response.url
            product_url = context.request.user_data.get("product_url", "")
            product_num = context.request.user_data.get("product_num", 0)

            context.log.info(f"")
            context.log.info(f"   ========================================")
            context.log.info(f"   📥 HANDLER ITEM_IMG APPELÉ")
            context.log.info(f"   Product #: {product_num}")
            context.log.info(f"   URL: {img_url}")
            context.log.info(f"   ========================================")

            try:
                # Créer le sous-dossier du produit
                product_dir = self.images_dir / f"product_{product_num:03d}"
                context.log.info(f"      Création dossier: {product_dir}")
                product_dir.mkdir(parents=True, exist_ok=True)
                context.log.info(f"      ✅ Dossier existe")

                # Incrémenter le compteur d'images pour ce produit
                if product_num not in self.product_image_counters:
                    self.product_image_counters[product_num] = 0
                self.product_image_counters[product_num] += 1
                img_num = self.product_image_counters[product_num]
                context.log.info(f"      Numéro d'image pour ce produit: {img_num}")

                # Déterminer l'extension
                ext = '.jpg'
                parsed = urlparse(img_url)
                file_ext = os.path.splitext(parsed.path)[1]
                if file_ext in ['.jpg', '.jpeg', '.png', '.webp']:
                    ext = file_ext
                context.log.info(f"      Extension: {ext}")

                # Nom de fichier
                filename = f"image_{img_num}{ext}"
                filepath = product_dir / filename
                context.log.info(f"      Chemin complet: {filepath}")

                # Télécharger l'image via response.body()
                if not filepath.exists():
                    context.log.info(f"      Appel response.body()...")
                    data = await context.response.body()
                    context.log.info(f"      Données reçues: {len(data) if data else 0} bytes")

                    if data and len(data) > 0:
                        context.log.info(f"      Écriture dans fichier...")
                        # Écriture atomique avec flush et fsync
                        with open(filepath, 'wb') as f:
                            f.write(data)
                            f.flush()
                            os.fsync(f.fileno())
                        context.log.info(f"      Écriture terminée")

                        # Vérifier que le fichier existe
                        if filepath.exists():
                            actual_size = filepath.stat().st_size
                            context.log.info(f"   ✅ ✅ ✅ IMAGE TÉLÉCHARGÉE: {filename} ({actual_size} bytes)")

                            # Sauvegarder les métadonnées
                            img_metadata = {
                                "src": img_url,
                                "link": product_url,
                                "local_path": str(filepath),
                            }
                            await img_dataset.push_data(img_metadata)
                            context.log.info(f"      ✅ Métadonnées sauvegardées")
                        else:
                            context.log.error(f"   ❌ FICHIER NON CRÉÉ après écriture!")
                    else:
                        context.log.error(f"   ❌ DONNÉES VIDES de response.body()")
                else:
                    context.log.info(f"   ⏭️ Image déjà existante: {filename}")

            except Exception as e:
                context.log.error(f"   ❌ ❌ ❌ ERREUR HANDLER: {str(e)}")
                import traceback
                context.log.error(f"   Traceback complet:")
                context.log.error(f"{traceback.format_exc()}")

            await context.page.close()
            context.log.info(f"   Page fermée")
            context.log.info(f"   ========================================")
            context.log.info(f"")

        # ========================
        # HANDLER: Requêtes bloquées par robots.txt
        # ========================
        @crawler.on_skipped_request
        async def skipped_request_handler(url: str, reason: SkippedReason) -> None:
            if reason == "robots_txt":
                crawler.log.info(f"⚠️ Bloqué par robots.txt: {url}")

        # ========================
        # Démarrer le crawl
        # ========================
        start_url = "https://www.aliexpress.com"
        crawler.log.info(f"🚀 Démarrage du crawl: {start_url}")
        crawler.log.info(f"   📸 Image: {image_path}")
        crawler.log.info(f"   🎯 Objectif: {max_results} produits")

        await crawler.run([start_url], purge_request_queue=True)

        # ========================
        # Exporter les résultats
        # ========================
        crawler.log.info("💾 Export des données...")

        items_json = self.output_dir / "product_data.json"
        images_json = self.output_dir / "image_metadata.json"

        await crawler.export_data(
            path=str(items_json),
            dataset_name=f"{self.attempt_id}-items"
        )
        await crawler.export_data(
            path=str(images_json),
            dataset_name=f"{self.attempt_id}-images"
        )

        crawler.log.info(f"✅ Items exportés: {items_json}")
        crawler.log.info(f"✅ Images exportées: {images_json}")

        # Charger et retourner les données
        image_metadata_list = []
        product_data_list = []

        # Lire les fichiers JSON exportés
        import json

        if items_json.exists():
            with open(items_json, 'r', encoding='utf-8') as f:
                items_data = json.load(f)
                for item in items_data:
                    product_data_list.append(ProductData(
                        item_url=item['item_url'],
                        collection_date=datetime.fromisoformat(item['collection_date']),
                        src_image=item['src_image'],
                        title=item['title'],
                        description=item['description'],
                        price=item['price'],
                        screenshot_path=item['screenshot_path'],
                        product_image_paths=item['product_image_paths']
                    ))

        if images_json.exists():
            with open(images_json, 'r', encoding='utf-8') as f:
                images_data = json.load(f)
                for img in images_data:
                    image_metadata_list.append(ImageMetadata(
                        src=img['src'],
                        link=img['link']
                    ))

        return image_metadata_list, product_data_list

    async def _extract_search_results(
        self,
        context: PlaywrightCrawlingContext,
        item_dataset: Dataset,
        request_queue: RequestQueue
    ) -> None:
        """
        Extrait les liens produits depuis une page de résultats
        """
        page = context.page
        context.log.info("🔍 Extraction des résultats de recherche...")

        try:
            # Attendre que les produits se chargent
            await page.wait_for_timeout(2000)

            # Trouver tous les liens produits
            # AliExpress utilise généralement .search-card-item
            selectors = [
                ".search-card-item",
                "a[href*='/item/']",
                "div[class*='product'] a",
                "div[class*='item'] a",
            ]

            links = []
            for selector in selectors:
                try:
                    elements = await page.locator(selector).all()
                    if elements and len(elements) > 5:
                        links = elements
                        context.log.info(f"   ✅ {len(links)} résultats avec: {selector}")
                        break
                except:
                    continue

            if not links:
                context.log.warning("   ⚠️ Aucun résultat trouvé")
                return

            # Extraire les URLs
            product_urls = []
            for link in links[:self.target_results]:  # Limiter
                try:
                    href = await link.get_attribute("href")
                    if href and '/item/' in href:
                        if not href.startswith('http'):
                            href = urljoin(page.url, href)
                        # Nettoyer l'URL
                        clean_url = url_noparams(href)
                        if clean_url not in product_urls:
                            product_urls.append(clean_url)
                except:
                    continue

            context.log.info(f"   📦 {len(product_urls)} produits uniques extraits")

            # Ajouter les requêtes pour chaque produit
            for product_url in product_urls:
                await context.add_requests([
                    Request.from_url(product_url, label="ITEM")
                ])

        except Exception as e:
            context.log.error(f"   ❌ Erreur extraction: {e}")


async def search_aliexpress_by_image(
    image_path: str,
    category: str = "",
    output_dir: str = "output",
    max_results: int = 50
) -> Tuple[List[ImageMetadata], List[ProductData]]:
    """
    Rechercher sur AliExpress par upload d'image

    Args:
        image_path: Chemin vers l'image
        category: Catégorie (non utilisé avec upload d'image)
        output_dir: Répertoire de sortie
        max_results: Nombre max de résultats

    Returns:
        Tuple de (image_metadata_list, product_data_list)
    """
    scraper = AliExpressImageSearchScraper(output_dir)
    return await scraper.search_by_image(image_path, category, max_results)
