/**
 * Application principale React
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import ImageSearch from './pages/ImageSearch';
import './styles/App.css';

const App: React.FC = () => {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <main className="pt-16">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/image-search" element={<ImageSearch />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-luxury-black text-white py-8">
          <div className="max-w-7xl mx-auto px-4 text-center">
            <p className="font-montserrat text-sm text-gray-400">
              💎 Luxury AI Search v1.0 | Propulsé par Intelligence Artificielle
            </p>
            <p className="font-montserrat text-xs text-gray-500 mt-2">
              Modèles PyTorch en cache pour performance optimale
            </p>
          </div>
        </footer>
      </div>
    </Router>
  );
};

export default App;
