import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
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
    ChevronRight,
    Leaf,
    Clock,
    AlertTriangle
} from 'lucide-react';
import { toast } from 'react-toastify';

export function ProductDetails() {
    const { productId } = useParams();
    const navigate = useNavigate();
    const location = useLocation();

    // Fix: Prioritize state passed from search page (Correct Logic)
    const [product, setProduct] = useState(location.state?.product || null);

    const [loading, setLoading] = useState(!location.state?.product);
    const [error, setError] = useState(null);
    const [wastageInfo, setWastageInfo] = useState(null);
    const [analyzing, setAnalyzing] = useState(false);

    useEffect(() => {
        const loadData = async () => {
            // 1. If no product in state, we have to fetch (which might be mock or error)
            if (!product) {
                setLoading(true);
                try {
                    const response = await shoppingApi.getProduct(productId);
                    if (response.success) {
                        setProduct(response.product);
                    } else {
                        setError('Product not found');
                    }
                } catch (err) {
                    setError('Failed to load product details');
                } finally {
                    setLoading(false);
                }
            }

            // 2. Fetch Wastage Intelligence (The Unique Feature)
            if (product || location.state?.product) {
                const targetName = product?.name || location.state?.product?.name;
                if (targetName) {
                    setAnalyzing(true);
                    try {
                        const res = await shoppingApi.analyzeProduct(targetName);
                        if (res.success) {
                            setWastageInfo(res.analysis);
                        }
                    } catch (e) {
                        console.error("Wastage analysis failed", e);
                    } finally {
                        setAnalyzing(false);
                    }
                }
            }
        };

        loadData();
    }, [productId]); // Run once or when ID changes

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
                                <div className="aspect-square rounded-xl overflow-hidden bg-gray-100 p-4 flex items-center justify-center">
                                    <img
                                        src={product.image}
                                        alt={product.name}
                                        className="max-h-full max-w-full object-contain hover:scale-105 transition-transform duration-500"
                                    />
                                </div>
                            </div>

                            {/* Info Section */}
                            <div className="flex flex-col">
                                <div className="flex items-center space-x-2 text-sm text-[#2D9B81] font-semibold mb-2">
                                    <span>{product.store}</span>
                                    <ChevronRight size={14} />
                                    <span className="text-gray-500 uppercase tracking-wider">Kitchen Essentials</span>
                                </div>

                                <h1 className="text-3xl md:text-4xl font-bold text-[#1E5245] mb-4">
                                    {product.name}
                                </h1>

                                <div className="flex items-center space-x-4 mb-6">
                                    <div className="flex items-center text-yellow-400 bg-yellow-50 px-3 py-1 rounded-full">
                                        <Star size={18} fill="currentColor" />
                                        <span className="ml-1 font-bold text-yellow-700">{product.rating || 4.5}</span>
                                    </div>
                                    <span className="text-gray-500">{product.reviews || 0} customer reviews</span>
                                </div>

                                <div className="text-4xl font-bold text-[#2D9B81] mb-6">
                                    ${product.price}
                                </div>

                                <div className="grid grid-cols-2 gap-4 mb-8">
                                    <div className="flex items-center p-4 bg-green-50 rounded-xl border border-green-100">
                                        <CheckCircle className="text-green-500 mr-3" size={24} />
                                        <div>
                                            <div className="text-sm font-semibold text-green-800">Available</div>
                                            <div className="text-xs text-green-600">In Stock</div>
                                        </div>
                                    </div>
                                    <div className="flex items-center p-4 bg-blue-50 rounded-xl border border-blue-100">
                                        <Truck className="text-blue-500 mr-3" size={24} />
                                        <div>
                                            <div className="text-sm font-semibold text-blue-800">Delivery</div>
                                            <div className="text-xs text-blue-600">Standard Shipping</div>
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
                                        <ShoppingCart className="mr-2" /> Add to Kitchen Inventory
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* UNIQUE FEATURE: WASTAGE MANAGEMENT GUIDANCE */}
                        <div className="border-t border-gray-100 p-8 md:p-10 bg-gradient-to-r from-[#E8F8F3] to-white relative overflow-hidden">
                            <div className="absolute top-0 right-0 -mt-8 -mr-8 text-[#2D9B81] opacity-10 transform rotate-12">
                                <Leaf size={200} fill="currentColor" />
                            </div>

                            <div className="relative z-10">
                                <div className="flex items-center space-x-2 mb-6">
                                    <span className="bg-[#2D9B81] text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-widest flex items-center">
                                        <Leaf size={12} className="mr-1" /> Eco-Smart
                                    </span>
                                    <h2 className="text-2xl font-bold text-[#1E5245]">Preparation & Wastage Guidance</h2>
                                </div>

                                {analyzing ? (
                                    <div className="flex items-center justify-center h-24">
                                        <div className="animate-pulse text-[#2D9B81] font-medium">Running AI Waste Analysis...</div>
                                    </div>
                                ) : wastageInfo ? (
                                    <div className="grid md:grid-cols-3 gap-6">
                                        {/* Shelf Life */}
                                        <div className="bg-white p-5 rounded-xl shadow-sm border border-green-100">
                                            <div className="text-gray-500 text-sm mb-2 uppercase tracking-wider font-semibold flex items-center">
                                                <Clock size={16} className="mr-2 text-green-600" />
                                                Estimated Shelf Life
                                            </div>
                                            <div className="text-2xl font-bold text-[#1E5245]">{wastageInfo.shelf_life}</div>
                                            <p className="text-xs text-gray-500 mt-2">
                                                Plan your usage within this window to avoid spoilage.
                                            </p>
                                        </div>

                                        {/* Storage Tip */}
                                        <div className="bg-white p-5 rounded-xl shadow-sm border border-green-100">
                                            <div className="text-gray-500 text-sm mb-2 uppercase tracking-wider font-semibold flex items-center">
                                                <Info size={16} className="mr-2 text-blue-600" />
                                                Smart Storage Tip
                                            </div>
                                            <p className="text-md font-medium text-[#1E5245] leading-snug">
                                                "{wastageInfo.storage_tip}"
                                            </p>
                                        </div>

                                        {/* Buying Advice */}
                                        <div className="bg-white p-5 rounded-xl shadow-sm border border-green-100">
                                            <div className="text-gray-500 text-sm mb-2 uppercase tracking-wider font-semibold flex items-center">
                                                <AlertTriangle size={16} className="mr-2 text-orange-500" />
                                                Wastage Risk: <span className="ml-1 text-black">{wastageInfo.wastage_risk}</span>
                                            </div>
                                            <p className="text-sm text-gray-600 mt-1 italic">
                                                Eco-Tip: {wastageInfo.eco_tip}
                                            </p>
                                            <div className={`w-full h-1.5 rounded-full mt-3 overflow-hidden ${wastageInfo.wastage_risk === 'High' ? 'bg-red-100' : 'bg-green-100'
                                                }`}>
                                                <div className={`h-full w-[${wastageInfo.wastage_risk === 'High' ? '80%' : '30%'}] ${wastageInfo.wastage_risk === 'High' ? 'bg-red-500' : 'bg-green-500'
                                                    }`}></div>
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="text-gray-500 text-center">Unable to load wastage data.</div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <ChatAssistant />
        </div>
    );
}
