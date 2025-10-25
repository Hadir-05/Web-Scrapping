/**
 * Barre de navigation
 */
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FiSearch, FiImage, FiInfo } from 'react-icons/fi';

const Navbar: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  const navItems = [
    { path: '/', label: 'Recherche Texte', icon: FiSearch },
    { path: '/image-search', label: 'Recherche Image', icon: FiImage },
  ];

  return (
    <nav className="bg-luxury-black shadow-gold fixed w-full top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link
            to="/"
            className="flex items-center space-x-2 text-gold-500 hover:text-gold-400 transition-colors"
          >
            <span className="text-2xl">💎</span>
            <span className="text-xl font-playfair font-bold">
              Luxury AI Search
            </span>
          </Link>

          {/* Nav Items */}
          <div className="flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-montserrat font-medium transition-all ${
                    isActive(item.path)
                      ? 'bg-gold-500 text-black'
                      : 'text-white hover:bg-gray-800'
                  }`}
                >
                  <Icon size={18} />
                  <span className="hidden sm:inline">{item.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
