import React, { useState } from 'react';
import { Sidebar } from '../components/Sidebar';
import { SearchBar } from '../components/SearchBar';
import { FilterPanel } from '../components/FilterPanel';
import { ProductCard } from '../components/ProductCard';
import { ChatAssistant } from '../components/ChatAssistant';
import { useHistory } from '../context/HistoryContext';

const mockProducts = [
  {
    id: '1',
    name: 'Wireless Bluetooth Headphones',
    price: 79.99,
    rating: 4.5,
    image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400',
    category: 'electronics',
    aiReason: 'Recommended because of high ratings and wireless features'
  },
  {
    id: '2',
    name: 'Smart Fitness Watch',
    price: 199.99,
    rating: 4.8,
    image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400',
    category: 'electronics',
    aiReason: 'Popular choice for fitness enthusiasts'
  },
  {
    id: '3',
    name: 'Eco-Friendly Water Bottle',
    price: 24.99,
    rating: 4.3,
    image: 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400',
    category: 'home',
    aiReason: 'Sustainable and highly rated'
  },
  {
    id: '4',
    name: 'Laptop Backpack',
    price: 49.99,
    rating: 4.6,
    image: 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400',
    category: 'fashion',
    aiReason: 'Perfect for professionals and students'
  }
];

export function Search() {
  const [products] = useState(mockProducts);
  const [filters, setFilters] = useState({});
  const { addToHistory } = useHistory();

  const handleSearch = (query) => {
    addToHistory(query, filters);
    console.log('Searching for:', query);
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    console.log('Filters applied:', newFilters);
  };

  return (
    <div className="min-h-screen bg-[#E8F8F3]">
      <Sidebar />
      <div className="ml-64 min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <SearchBar onSearch={handleSearch} />
          </div>
          <div className="grid lg:grid-cols-4 gap-8">
            <div className="lg:col-span-1">
              <FilterPanel onFilterChange={handleFilterChange} />
            </div>
            <div className="lg:col-span-3">
              <div className="mb-4 flex justify-between items-center">
                <h2 className="text-2xl font-bold text-[#1E5245]">
                  AI Recommendations
                </h2>
                <select className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#2D9B81]">
                  <option>Relevance</option>
                  <option>Price: Low to High</option>
                  <option>Price: High to Low</option>
                  <option>Highest Rated</option>
                </select>
              </div>
              <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
                {products.map(product => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    onSave={() => console.log('Saved:', product.name)}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
      <ChatAssistant />
    </div>
  );
}

