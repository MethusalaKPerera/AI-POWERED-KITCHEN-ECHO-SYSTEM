import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';
import { SearchBar } from '../components/SearchBar';
import { FilterPanel } from '../components/FilterPanel';
import { ProductCard } from '../components/ProductCard';
import { ChatAssistant } from '../components/ChatAssistant';
import { useHistory } from '../context/HistoryContext';
import { useLanguage } from '../context/LanguageContext';
import { shoppingApi } from '../../../services/api';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { Loader2, AlertCircle } from 'lucide-react';

export function Search() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    minPrice: 0,
    maxPrice: 1000,
    category: '',
    sortBy: 'relevance',
    country: 'us'
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 12,
    total: 0
  });

  const { addToHistory } = useHistory();
  const { translations } = useLanguage();
  const navigate = useNavigate();
  const location = useLocation();

  // Handle URL query parameters
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const query = params.get('q');
    if (query) {
      setSearchQuery(query);
    }
  }, [location.search]);

  // Fetch products when search query or filters change
  useEffect(() => {
    if (searchQuery) {
      fetchProducts();
    } else {
      setProducts([]);
      setPagination(prev => ({
        ...prev,
        total: 0
      }));
    }
  }, [searchQuery, filters, pagination.page]);

  const fetchProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await shoppingApi.search(searchQuery, {
        minPrice: filters.minPrice,
        maxPrice: filters.maxPrice,
        category: filters.category,
        sortBy: filters.sortBy,
        minRating: filters.minRating || 0,
        inStock: filters.inStock || false,
        freeShipping: filters.freeShipping || false,
        onSale: filters.onSale || false,
        country: filters.country,
        page: pagination.page,
        pageSize: pagination.pageSize
      });

      const responseData = response.products ? response : { products: response, total: response.length || 0 };

      setProducts(responseData.products || responseData || []);
      setPagination(prev => ({
        ...prev,
        total: responseData.total || (responseData.products ? responseData.products.length : 0)
      }));

      // Note: Backend automatically saves search to history on GET /api/shopping/search
    } catch (err) {
      console.error('Error fetching products:', err);
      setError('Failed to fetch products. Please try again.');
      toast.error('Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = useCallback((query) => {
    setSearchQuery(query);
    setPagination(prev => ({ ...prev, page: 1 }));
  }, []);

  const handleFilterChange = useCallback((newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    setPagination(prev => ({ ...prev, page: 1 }));
  }, []);

  const handlePageChange = useCallback((newPage) => {
    setPagination(prev => ({ ...prev, page: newPage }));
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="min-h-screen bg-[#E8F8F3]">
      <Sidebar />
      <div className="md:ml-64 min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <SearchBar onSearch={handleSearch} initialValue={searchQuery} />
          </div>

          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded">
              <div className="flex">
                <div className="flex-shrink-0">
                  <AlertCircle className="h-5 w-5 text-red-500" />
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          <div className="grid lg:grid-cols-4 gap-8">
            <div className="lg:col-span-1">
              <FilterPanel
                onFilterChange={handleFilterChange}
                initialFilters={filters}
              />
            </div>

            <div className="lg:col-span-3">
              <div className="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <h2 className="text-2xl font-bold text-[#1E5245]">
                  {searchQuery ? `Results for "${searchQuery}"` : 'Popular Products'}
                  {products.length > 0 && (
                    <span className="ml-2 text-sm font-normal text-gray-500">
                      ({pagination.total} {pagination.total === 1 ? 'item' : 'items'})
                    </span>
                  )}
                </h2>

                <div className="flex items-center space-x-2">
                  <label htmlFor="sort" className="text-sm font-medium text-gray-700">
                    {translations.sortBy}:
                  </label>
                  <select
                    id="sort"
                    value={filters.sortBy}
                    onChange={(e) => handleFilterChange({ sortBy: e.target.value })}
                    className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#2D9B81] text-sm"
                  >
                    <option value="relevance">{translations.relevance}</option>
                    <option value="price_low">{translations.priceLowToHigh}</option>
                    <option value="price_high">{translations.priceHighToLow}</option>
                    <option value="rating">{translations.rating}</option>
                  </select>
                </div>
              </div>

              {loading ? (
                <div className="flex justify-center items-center h-64">
                  <Loader2 className="h-12 w-12 animate-spin text-[#2D9B81]" />
                </div>
              ) : products.length > 0 ? (
                <>
                  <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {products.map((product) => (
                      <ProductCard
                        key={product.id}
                        product={product}
                        onSave={(e) => {
                          e.stopPropagation();
                          console.log('Saved:', product.name);
                          toast.success(`Saved ${product.name} to your list`);
                        }}
                      />
                    ))}
                  </div>

                  {pagination.total > pagination.pageSize && (
                    <div className="mt-8 flex justify-center">
                      <nav className="flex items-center space-x-2">
                        {Array.from({ length: Math.ceil(pagination.total / pagination.pageSize) }).map((_, i) => (
                          <button
                            key={i}
                            onClick={() => handlePageChange(i + 1)}
                            className={`px-4 py-2 rounded-md ${pagination.page === i + 1
                              ? 'bg-[#2D9B81] text-white'
                              : 'bg-white text-gray-700 hover:bg-gray-100'
                              }`}
                          >
                            {i + 1}
                          </button>
                        ))}
                      </nav>
                    </div>
                  )}
                </>
              ) : searchQuery ? (
                <div className="text-center py-12">
                  <p className="text-gray-500 text-lg">
                    No products found for "{searchQuery}". Try a different search term.
                  </p>
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-gray-500 text-lg">
                    Start by searching for products above.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      <ChatAssistant />
    </div>
  );
}
