/**
 * Carte produit élégante
 */
import React from 'react';
import { motion } from 'framer-motion';
import { ProductResult } from '../services/api';

interface ProductCardProps {
  product: ProductResult;
  index: number;
}

const ProductCard: React.FC<ProductCardProps> = ({ product, index }) => {
  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
    }).format(price);
  };

  const formatScore = (score?: number): string => {
    if (!score) return 'N/A';
    return `${(score * 100).toFixed(0)}%`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
      className="bg-white rounded-xl shadow-lg hover:shadow-gold-lg transition-all duration-300 overflow-hidden group"
    >
      {/* Image */}
      <div className="relative h-64 overflow-hidden bg-luxury-gray">
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = 'https://via.placeholder.com/300x300?text=No+Image';
          }}
        />

        {/* Badge Score/Similarité */}
        {(product.score || product.similarity) && (
          <div className="absolute top-4 right-4 bg-gold-500 text-black px-3 py-1 rounded-full text-sm font-semibold">
            {formatScore(product.score || product.similarity)}
          </div>
        )}
      </div>

      {/* Contenu */}
      <div className="p-6">
        {/* ID Produit */}
        <p className="text-gold-600 text-xs font-montserrat uppercase tracking-wider mb-2">
          {product.product_id}
        </p>

        {/* Nom */}
        <h3 className="text-xl font-playfair font-semibold text-luxury-darkGray mb-2 line-clamp-1">
          {product.name}
        </h3>

        {/* Description */}
        {product.description && (
          <p className="text-gray-600 text-sm font-montserrat mb-4 line-clamp-2">
            {product.description}
          </p>
        )}

        {/* Prix */}
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
          <span className="text-2xl font-playfair font-bold text-gold-500">
            {formatPrice(product.price)}
          </span>

          <button className="bg-luxury-black text-white px-6 py-2 rounded-lg hover:bg-gold-500 hover:text-black transition-colors duration-300 font-montserrat font-medium text-sm">
            Voir Détails
          </button>
        </div>
      </div>
    </motion.div>
  );
};

export default ProductCard;
