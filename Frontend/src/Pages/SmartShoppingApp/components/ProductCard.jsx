import React from 'react';
import { useNavigate } from 'react-router-dom';
import { StarIcon, BookmarkIcon, ExternalLink } from 'lucide-react';
import { useCurrency } from '../context/CurrencyContext';

export function ProductCard({ product, onSave }) {
  const { convertPrice } = useCurrency();
  const navigate = useNavigate();

  const handleCardClick = (e) => {
    // Don't navigate if clicking an action button
    if (e.target.closest('button')) return;

    // Navigate to our internal detail page
    navigate(`/smart-shopping/product/${product.id}`);
  };

  return (
    <div
      className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 group cursor-pointer"
      onClick={handleCardClick}
    >
      <div className="relative overflow-hidden">
        <img
          src={product.image}
          alt={product.name}
          className="w-full h-48 object-cover group-hover:scale-110 transition-transform duration-300"
        />
        {product.store && (
          <div className="absolute top-2 right-2 bg-white px-3 py-1 rounded-full shadow-md">
            <span className="text-xs font-semibold text-[#2D5F4F]">{product.store}</span>
          </div>
        )}
        {(product.aiReason || product.recommended_by) && (
          <div className="absolute inset-0 bg-black bg-opacity-80 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center p-4">
            <p className="text-white text-sm text-center">
              {product.aiReason || `Recommended because you searched for "${product.recommended_by}"`}
            </p>
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
        <div className="flex gap-2">
          <button
            onClick={onSave}
            className="flex-1 flex items-center justify-center space-x-2 bg-[#2D9B81] text-white py-2 rounded-md hover:bg-[#267A68] transition-colors"
          >
            <BookmarkIcon size={16} />
            <span>Save</span>
          </button>
          {product.url && product.url !== '#' && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                window.open(product.url, '_blank', 'noopener,noreferrer');
              }}
              className="px-4 py-2 bg-white border-2 border-[#2D9B81] text-[#2D9B81] rounded-md hover:bg-[#D4F1E8] transition-colors"
              title="Visit store"
            >
              <ExternalLink size={16} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

