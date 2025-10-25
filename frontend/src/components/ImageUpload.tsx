/**
 * Composant d'upload d'image élégant
 */
import React, { useState, useRef } from 'react';
import { FiUpload, FiX, FiImage } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';

interface ImageUploadProps {
  onUpload: (file: File) => void;
  isLoading?: boolean;
}

const ImageUpload: React.FC<ImageUploadProps> = ({ onUpload, isLoading = false }) => {
  const [preview, setPreview] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (file: File) => {
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
      onUpload(file);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFileChange(file);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const file = e.dataTransfer.files?.[0];
    if (file) handleFileChange(file);
  };

  const handleClear = () => {
    setPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleInputChange}
        className="hidden"
        disabled={isLoading}
      />

      <AnimatePresence mode="wait">
        {!preview ? (
          <motion.div
            key="upload-zone"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-300 ${
              dragActive
                ? 'border-gold-500 bg-gold-50'
                : 'border-gray-300 hover:border-gold-500 hover:bg-gray-50'
            }`}
          >
            <FiUpload className="mx-auto text-6xl text-gold-500 mb-4" />
            <h3 className="text-xl font-playfair font-semibold text-luxury-darkGray mb-2">
              Téléchargez une image
            </h3>
            <p className="text-gray-600 font-montserrat">
              Glissez-déposez ou cliquez pour sélectionner
            </p>
            <p className="text-sm text-gray-400 mt-2 font-montserrat">
              JPG, PNG - Max 10MB
            </p>
          </motion.div>
        ) : (
          <motion.div
            key="preview"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="relative"
          >
            <div className="relative rounded-xl overflow-hidden shadow-gold">
              <img
                src={preview}
                alt="Preview"
                className="w-full h-96 object-contain bg-gray-100"
              />

              {isLoading && (
                <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                  <div className="text-center">
                    <div className="animate-spin h-12 w-12 border-4 border-gold-500 border-t-transparent rounded-full mx-auto mb-4" />
                    <p className="text-white font-montserrat font-semibold">
                      Analyse en cours...
                    </p>
                  </div>
                </div>
              )}
            </div>

            <button
              onClick={handleClear}
              disabled={isLoading}
              className="absolute -top-3 -right-3 bg-red-500 text-white p-2 rounded-full hover:bg-red-600 transition-colors disabled:opacity-50"
            >
              <FiX size={20} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ImageUpload;
