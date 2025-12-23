import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';
import { ChatAssistant } from '../components/ChatAssistant';
import { shoppingApi } from '../../../services/api';
import {
    ArrowLeft,
    Star,
    ShoppingCart,
    Truck,
    CheckCircle,
    Info,
    ChevronRight
} from 'lucide-react';
import { toast } from 'react-toastify';

export function ProductDetails() {
    const { productId } = useParams();
    const navigate = useNavigate();
    const [product, setProduct] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchProductDetails = async () => {
            setLoading(true);
            try {
                const response = await shoppingApi.getProduct(productId);
                if (response.success) {
                    setProduct(response.product);
                } else {
                    setError('Product not found');
                }
            } catch (err) {
                console.error('Error fetching product details:', err);
                setError('Failed to load product details');
            } finally {
                setLoading(false);
            }
        };
        fetchProductDetails();
    }, [productId]);

    if (loading) {
        return (
            <div className="min-h-screen bg-[#E8F8F3] flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#2D9B81]"></div>
            </div>
        );
    }

    if (error || !product) {
        return (
            <div className="min-h-screen bg-[#E8F8F3] flex flex-col items-center justify-center p-4">
                <Info className="h-16 w-16 text-gray-400 mb-4" />
                <h2 className="text-2xl font-bold text-[#1E5245] mb-2">{error || 'Product Not Found'}</h2>
                <button
                    onClick={() => navigate('/smart-shopping/search')}
                    className="text-[#2D9B81] hover:underline flex items-center"
                >
                    <ArrowLeft size={16} className="mr-2" /> Back to Search
                </button>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#E8F8F3]">
            <Sidebar />
            <div className="md:ml-64 min-h-screen">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <button
                        onClick={() => navigate(-1)}
                        className="flex items-center text-[#2D5F4F] hover:text-[#2D9B81] transition-colors mb-6"
                    >
                        <ArrowLeft size={20} className="mr-2" /> Back
                    </button>

                    <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
                        <div className="grid md:grid-cols-2 gap-8 p-6 md:p-10">
                            {/* Image Section */}
                            <div className="space-y-4">
                                <div className="aspect-square rounded-xl overflow-hidden bg-gray-100">
                                    <img
                                        src={product.image}
                                        alt={product.name}
                                        className="w-full h-full object-cover"
                                    />
                                </div>
                            </div>

                            {/* Info Section */}
                            <div className="flex flex-col">
                                <div className="flex items-center space-x-2 text-sm text-[#2D9B81] font-semibold mb-2">
                                    <span>{product.store}</span>
                                    <ChevronRight size={14} />
                                    <span className="text-gray-500 uppercase tracking-wider">Premium Selection</span>
                                </div>

                                <h1 className="text-3xl md:text-4xl font-bold text-[#1E5245] mb-4">
                                    {product.name}
                                </h1>

                                <div className="flex items-center space-x-4 mb-6">
                                    <div className="flex items-center text-yellow-400 bg-yellow-50 px-3 py-1 rounded-full">
                                        <Star size={18} fill="currentColor" />
                                        <span className="ml-1 font-bold text-yellow-700">{product.rating}</span>
                                    </div>
                                    <span className="text-gray-500">{product.reviews} customer reviews</span>
                                </div>

                                <div className="text-4xl font-bold text-[#2D9B81] mb-6">
                                    ${product.price}
                                </div>

                                <p className="text-gray-600 text-lg mb-8 leading-relaxed">
                                    {product.description}
                                </p>

                                <div className="grid grid-cols-2 gap-4 mb-8">
                                    <div className="flex items-center p-4 bg-green-50 rounded-xl border border-green-100">
                                        <CheckCircle className="text-green-500 mr-3" size={24} />
                                        <div>
                                            <div className="text-sm font-semibold text-green-800">In Stock</div>
                                            <div className="text-xs text-green-600">{product.delivery}</div>
                                        </div>
                                    </div>
                                    <div className="flex items-center p-4 bg-blue-50 rounded-xl border border-blue-100">
                                        <Truck className="text-blue-500 mr-3" size={24} />
                                        <div>
                                            <div className="text-sm font-semibold text-blue-800">Free Delivery</div>
                                            <div className="text-xs text-blue-600">On all premium orders</div>
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    <button
                                        onClick={() => {
                                            toast.success(`Successfully added ${product.name} to cart!`);
                                        }}
                                        className="w-full bg-[#2D9B81] hover:bg-[#267A68] text-white py-4 rounded-xl font-bold text-lg flex items-center justify-center transition-all transform hover:scale-[1.02] shadow-lg shadow-green-100"
                                    >
                                        <ShoppingCart className="mr-2" /> Add to Shopping List
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Specs / Detailed Info */}
                        <div className="border-t border-gray-100 bg-gray-50 p-8 md:p-10">
                            <h2 className="text-2xl font-bold text-[#1E5245] mb-6">Technical Specifications</h2>
                            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
                                {(product.specs || []).map((spec, index) => (
                                    <div key={index} className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                                        <div className="text-sm text-gray-500 mb-1">{spec.label}</div>
                                        <div className="font-semibold text-[#1E5245]">{spec.value}</div>
                                    </div>
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
