import React from 'react';
import { StarIcon, BookmarkIcon } from 'lucide-react';
import { useCurrency } from '../context/CurrencyContext';

export function ProductCard({ product, onSave }) {
  const { convertPrice } = useCurrency();

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 group">
      <div className="relative overflow-hidden">
        <img
          src={product.image}
          alt={product.name}
          className="w-full h-48 object-cover group-hover:scale-110 transition-transform duration-300"
        />
        {product.aiReason && (
          <div className="absolute inset-0 bg-black bg-opacity-80 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center p-4">
            <p className="text-white text-sm text-center">{product.aiReason}</p>
          </div>
        )}
      </div>
      <div className="p-4">
        <h3 className="text-lg font-semibold text-[#1E5245] mb-2 line-clamp-2">
          {product.name}
        </h3>
        <div className="flex items-center justify-between mb-2">
          <span className="text-2xl font-bold text-[#2D9B81]">
            {convertPrice(product.price)}
          </span>
          <div className="flex items-center space-x-1">
            <StarIcon size={16} className="fill-yellow-400 text-yellow-400" />
            <span className="text-sm font-medium text-[#2D5F4F]">
              {product.rating}
            </span>
          </div>
        </div>
        {product.category && (
          <span className="inline-block px-3 py-1 bg-[#D4F1E8] text-[#2D5F4F] text-xs rounded-full mb-3">
            {product.category}
          </span>
        )}
        <button
          onClick={onSave}
          className="w-full flex items-center justify-center space-x-2 bg-[#2D9B81] text-white py-2 rounded-md hover:bg-[#267A68] transition-colors"
        >
          <BookmarkIcon size={16} />
          <span>Save to History</span>
        </button>
      </div>
    </div>
  );
}

