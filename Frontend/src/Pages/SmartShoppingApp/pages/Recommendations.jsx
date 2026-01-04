import React, { useState, useEffect } from 'react';
import { Sidebar } from '../components/Sidebar';
import { ProductCard } from '../components/ProductCard';
import { ChatAssistant } from '../components/ChatAssistant';
import { shoppingApi } from '../../../services/api';
import { Loader2, Sparkles } from 'lucide-react';

export function Recommendations() {
  const [sortBy, setSortBy] = useState('ai-suggested');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reason, setReason] = useState('Popular today');

  useEffect(() => {
    const fetchRecommendations = async () => {
      setLoading(true);
      try {
        const response = await shoppingApi.getRecommendations();
        if (response.success) {
          setRecommendations(response.recommendations || []);
          setReason(response.reason || 'Popular today');
        }
      } catch (error) {
        console.error('Failed to fetch recommendations:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, []);

  const sortedProducts = [...recommendations].sort((a, b) => {
    if (sortBy === 'price-low') return a.price - b.price;
    if (sortBy === 'price-high') return b.price - a.price;
    if (sortBy === 'rating') return b.rating - a.rating;
    return 0; // ai-suggested (original order)
  });

  return (
    <div className="min-h-screen bg-[#E8F8F3]">
      <Sidebar />
      <div className="md:ml-64 min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <div className="flex items-center space-x-2 text-[#2D9B81] mb-2 font-semibold tracking-wide uppercase text-sm">
              <Sparkles size={18} />
              <span>AI Powered Intelligence</span>
            </div>
            <h1 className="text-4xl font-bold text-[#1E5245] mb-2">
              Your Personalized Recommendations
            </h1>
            <p className="text-[#2D5F4F]">
              {reason}
            </p>
          </div>

          <div className="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <p className="text-[#2D5F4F]">
              {loading ? 'Finding the best products...' : `${recommendations.length} products recommended`}
            </p>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-[#1E5245]">Sort by:</span>
              <select
                value={sortBy}
                onChange={e => setSortBy(e.target.value)}
                className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#2D9B81] bg-white text-sm"
              >
                <option value="ai-suggested">AI Suggested</option>
                <option value="price-low">Lowest Price</option>
                <option value="price-high">Highest Price</option>
                <option value="rating">Highest Rated</option>
              </select>
            </div>
          </div>

          {loading ? (
            <div className="flex flex-col items-center justify-center h-64">
              <Loader2 className="h-12 w-12 animate-spin text-[#2D9B81] mb-4" />
              <p className="text-[#2D5F4F] font-medium">Analyzing your preferences...</p>
            </div>
          ) : recommendations.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {sortedProducts.map(product => (
                <ProductCard
                  key={product.id}
                  product={product}
                  onSave={() => console.log('Saved:', product.name)}
                />
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-2xl p-12 text-center shadow-sm border border-gray-100">
              <p className="text-gray-500 text-lg mb-4">
                We're still learning your style!
              </p>
              <button
                onClick={() => window.location.href = '/smart-shopping/search'}
                className="bg-[#2D9B81] text-white px-6 py-2 rounded-full font-semibold hover:bg-[#267A68] transition-colors"
              >
                Start Searching
              </button>
            </div>
          )}
        </div>
      </div>
      <ChatAssistant />
    </div>
  );
}

