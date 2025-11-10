import React, { useState } from 'react';
import { SlidersHorizontalIcon } from 'lucide-react';

export function FilterPanel({ onFilterChange }) {
  const [priceRange, setPriceRange] = useState([0, 1000]);
  const [rating, setRating] = useState(0);
  const [category, setCategory] = useState('');
  const [keyword, setKeyword] = useState('');

  const handleApply = () => {
    onFilterChange({
      priceRange,
      rating,
      category,
      keyword
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
      <div className="flex items-center space-x-2 text-lg font-semibold text-[#1E5245]">
        <SlidersHorizontalIcon size={20} />
        <h3>Filters</h3>
      </div>
      <div>
        <label className="block text-sm font-medium text-[#2D5F4F] mb-2">
          Keyword
        </label>
        <input
          type="text"
          value={keyword}
          onChange={e => setKeyword(e.target.value)}
          placeholder="e.g., wireless, eco-friendly"
          className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#2D9B81]"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-[#2D5F4F] mb-2">
          Price Range: ${priceRange[0]} - ${priceRange[1]}
        </label>
        <input
          type="range"
          min="0"
          max="1000"
          value={priceRange[1]}
          onChange={e => setPriceRange([priceRange[0], parseInt(e.target.value)])}
          className="w-full accent-[#2D9B81]"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-[#2D5F4F] mb-2">
          Minimum Rating
        </label>
        <select
          value={rating}
          onChange={e => setRating(parseInt(e.target.value))}
          className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#2D9B81]"
        >
          <option value="0">Any</option>
          <option value="1">1+ Stars</option>
          <option value="2">2+ Stars</option>
          <option value="3">3+ Stars</option>
          <option value="4">4+ Stars</option>
          <option value="5">5 Stars</option>
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium text-[#2D5F4F] mb-2">
          Category
        </label>
        <select
          value={category}
          onChange={e => setCategory(e.target.value)}
          className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#2D9B81]"
        >
          <option value="">All Categories</option>
          <option value="electronics">Electronics</option>
          <option value="fashion">Fashion</option>
          <option value="home">Home & Garden</option>
          <option value="sports">Sports & Outdoors</option>
          <option value="books">Books</option>
        </select>
      </div>
      <button
        onClick={handleApply}
        className="w-full bg-[#2D9B81] text-white py-2 rounded-md hover:bg-[#267A68] transition-colors"
      >
        Apply Filters
      </button>
    </div>
  );
}

