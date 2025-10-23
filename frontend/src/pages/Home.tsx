/**
 * Page d'accueil - Recherche par mots-clés
 */
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import SearchBar from '../components/SearchBar';
import ProductCard from '../components/ProductCard';
import { searchByKeyword, ProductResult } from '../services/api';

const Home: React.FC = () => {
  const [results, setResults] = useState<ProductResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (query: string) => {
    setIsLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const response = await searchByKeyword(query, 12);
      setResults(response.results);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la recherche');
      console.error('Search error:', err);
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
            <span className="text-gold-500">Luxury</span> AI Search
          </h1>
          <p className="text-xl font-montserrat text-gray-600 max-w-2xl mx-auto">
            Recherche intelligente pour produits de luxe
          </p>
        </motion.div>

        {/* Barre de recherche */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <SearchBar
            onSearch={handleSearch}
            isLoading={isLoading}
            placeholder="Sac à main en cuir, montre suisse, parfum floral..."
          />
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
                Recherche en cours...
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
                Aucun résultat trouvé
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
                  {results.length} Résultats Trouvés
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

export default Home;
