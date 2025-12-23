import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Home } from './pages/Home';
import { Search } from './pages/Search';
import { Recommendations } from './pages/Recommendations';
import { History } from './pages/History';
import { Settings } from './pages/Settings';
import { ProductDetails } from './pages/ProductDetails';

export function AppRouter() {
  return (
    <Routes>
      <Route path="" element={<Home />} />
      <Route path="search" element={<Search />} />
      <Route path="recommendations" element={<Recommendations />} />
      <Route path="history" element={<History />} />
      <Route path="settings" element={<Settings />} />
      <Route path="product/:productId" element={<ProductDetails />} />
    </Routes>
  );
}

