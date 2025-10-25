/**
 * Page de recherche par image
 */
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import ImageUpload from '../components/ImageUpload';
import ProductCard from '../components/ProductCard';
import { searchByImageUpload, ProductResult } from '../services/api';

const ImageSearch: React.FC = () => {
  const [results, setResults] = useState<ProductResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleImageUpload = async (file: File) => {
    setIsLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const response = await searchByImageUpload(file, 12);
      setResults(response.results);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la recherche');
      console.error('Image search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Hero Section */}
      <section className="pt-20 pb-12 px-4">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h1 className="text-6xl font-playfair font-bold text-luxury-darkGray mb-4">
            Recherche par <span className="text-gold-500">Image</span>
          </h1>
          <p className="text-xl font-montserrat text-gray-600 max-w-2xl mx-auto">
            Trouvez des produits similaires en téléchargeant une image
          </p>
        </motion.div>

        {/* Upload d'image */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <ImageUpload onUpload={handleImageUpload} isLoading={isLoading} />
        </motion.div>
      </section>

      {/* Résultats */}
      <section className="px-4 pb-20">
        <div className="max-w-7xl mx-auto">
          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-red-50 border-2 border-red-200 text-red-700 px-6 py-4 rounded-xl mb-8 font-montserrat"
            >
              {error}
            </motion.div>
          )}

          {isLoading && (
            <div className="text-center py-20">
              <div className="animate-spin h-16 w-16 border-4 border-gold-500 border-t-transparent rounded-full mx-auto mb-4" />
              <p className="text-xl font-montserrat text-gray-600">
                Analyse de l'image en cours...
              </p>
            </div>
          )}

          {!isLoading && hasSearched && results.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-20"
            >
              <p className="text-2xl font-playfair text-gray-500">
                Aucun produit similaire trouvé
              </p>
            </motion.div>
          )}

          {!isLoading && results.length > 0 && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mb-8"
              >
                <h2 className="text-3xl font-playfair font-semibold text-luxury-darkGray">
                  {results.length} Produits Similaires
                </h2>
              </motion.div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {results.map((product, index) => (
                  <ProductCard
                    key={product.product_id}
                    product={product}
                    index={index}
                  />
                ))}
              </div>
            </>
          )}
        </div>
      </section>
    </div>
  );
};

export default ImageSearch;
