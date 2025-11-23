import React, { useState } from 'react';
import { Sidebar } from '../components/Sidebar';
import { ProductCard } from '../components/ProductCard';
import { ChatAssistant } from '../components/ChatAssistant';

const recommendedProducts = [
  {
    id: '1',
    name: 'Premium Wireless Earbuds',
    price: 149.99,
    rating: 4.9,
    image: 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400',
    category: 'electronics',
    aiReason: 'Top choice based on your recent searches for audio devices'
  },
  {
    id: '2',
    name: 'Smart Home Hub',
    price: 99.99,
    rating: 4.7,
    image: 'https://images.unsplash.com/photo-1558089687-e5e5e5e5e5e5?w=400',
    category: 'electronics',
    aiReason: 'Complements your smart home setup'
  }
];

export function Recommendations() {
  const [sortBy, setSortBy] = useState('ai-suggested');

  return (
    <div className="min-h-screen bg-[#E8F8F3]">
      <Sidebar />
      <div className="ml-64 min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-[#1E5245] mb-2">
              Your Personalized Recommendations
            </h1>
            <p className="text-[#2D5F4F]">
              Curated just for you based on your preferences and search history
            </p>
          </div>
          <div className="mb-6 flex justify-between items-center">
            <p className="text-[#2D5F4F]">
              {recommendedProducts.length} products recommended
            </p>
            <select
              value={sortBy}
              onChange={e => setSortBy(e.target.value)}
              className="border border-gray-300 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#2D9B81]"
            >
              <option value="ai-suggested">AI Suggested</option>
              <option value="price-low">Lowest Price</option>
              <option value="price-high">Highest Price</option>
              <option value="rating">Highest Rated</option>
            </select>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {recommendedProducts.map(product => (
              <ProductCard
                key={product.id}
                product={product}
                onSave={() => console.log('Saved:', product.name)}
              />
            ))}
          </div>
        </div>
      </div>
      <ChatAssistant />
    </div>
  );
}

