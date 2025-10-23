/**
 * Barre de recherche élégante
 */
import React, { useState } from 'react';
import { FiSearch } from 'react-icons/fi';

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  isLoading?: boolean;
}

const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  placeholder = 'Rechercher des produits de luxe...',
  isLoading = false,
}) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-4xl mx-auto">
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          disabled={isLoading}
          className="w-full px-6 py-4 pr-32 text-lg font-montserrat border-2 border-gold-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-gold-400 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed transition-all"
        />

        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 bg-gold-500 text-black px-6 py-2 rounded-lg hover:bg-gold-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-300 flex items-center gap-2 font-montserrat font-semibold"
        >
          {isLoading ? (
            <>
              <div className="animate-spin h-5 w-5 border-2 border-black border-t-transparent rounded-full" />
              <span>Recherche...</span>
            </>
          ) : (
            <>
              <FiSearch size={20} />
              <span>Rechercher</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
};

export default SearchBar;
