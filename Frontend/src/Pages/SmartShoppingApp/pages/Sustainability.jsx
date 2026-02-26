import React, { useState, useEffect } from 'react';
import { Sidebar } from '../components/Sidebar';
import { ChatAssistant } from '../components/ChatAssistant';
import {
    Leaf,
    TrendingDown,
    BarChart3,
    Target,
    CheckCircle2,
    AlertCircle,
    Info,
    ArrowUpRight,
    Globe
} from 'lucide-react';

export function Sustainability() {
    const [stats, setStats] = useState({
        wasteReduced: '73.9%',
        accuracy: '86.8%',
        matchingRate: '75%',
        moneySaved: '$492',
        carbonFootprint: '-12kg',
        ecoScore: 84
    });

    const [loading, setLoading] = useState(false);

    const metrics = [
        {
            title: "Food Waste Reduction",
            value: stats.wasteReduced,
            desc: "73.9% decrease from 2.3 to 0.6 kg weekly",
            icon: TrendingDown,
            color: "text-green-600",
            bg: "bg-green-50"
        },
        {
            title: "Search Accuracy",
            value: stats.accuracy,
            desc: "AI Classification Model Accuracy",
            icon: Target,
            color: "text-blue-600",
            bg: "bg-blue-50"
        },
        {
            title: "Matching Efficiency",
            value: stats.matchingRate,
            desc: "Ingredient-Recipe fuzzy matching accuracy",
            icon: BarChart3,
            color: "text-purple-600",
            bg: "bg-purple-50"
        },
        {
            title: "Annual Savings",
            value: stats.moneySaved,
            desc: "Estimated annual savings per household",
            icon: CheckCircle2,
            color: "text-orange-600",
            bg: "bg-orange-50"
        }
    ];

    return (
        <div className="min-h-screen bg-[#E8F8F3]">
            <Sidebar />
            <div className="md:ml-64 min-h-screen">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <div className="mb-10">
                        <h1 className="text-4xl font-bold text-[#1E5245] mb-2 flex items-center">
                            <Leaf className="mr-3 text-[#2D9B81]" /> Sustainability & Research Insights
                        </h1>
                        <p className="text-[#2D5F4F] text-lg">
                            Track your environmental impact and AI shopping performance metrics.
                        </p>
                    </div>

                    {/* Main Stats Grid */}
                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
                        {metrics.map((m, i) => (
                            <div key={i} className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div className={`${m.bg} ${m.color} w-12 h-12 rounded-xl flex items-center justify-center mb-4`}>
                                    <m.icon size={24} />
                                </div>
                                <div className="text-3xl font-bold text-[#1E5245] mb-1">{m.value}</div>
                                <div className="text-sm font-semibold text-gray-800 mb-1">{m.title}</div>
                                <p className="text-xs text-gray-500">{m.desc}</p>
                            </div>
                        ))}
                    </div>

                    <div className="grid lg:grid-cols-3 gap-8">
                        {/* Sustainability Score */}
                        <div className="lg:col-span-1 bg-white p-8 rounded-3xl shadow-lg border border-green-100 flex flex-col items-center justify-center text-center">
                            <div className="relative w-48 h-48 mb-6">
                                <svg className="w-full h-full transform -rotate-90">
                                    <circle
                                        cx="96" cy="96" r="80"
                                        stroke="currentColor" strokeWidth="12"
                                        fill="transparent" className="text-gray-100"
                                    />
                                    <circle
                                        cx="96" cy="96" r="80"
                                        stroke="currentColor" strokeWidth="12"
                                        fill="transparent" className="text-[#2D9B81]"
                                        strokeDasharray={2 * Math.PI * 80}
                                        strokeDashoffset={2 * Math.PI * 80 * (1 - stats.ecoScore / 100)}
                                        strokeLinecap="round"
                                    />
                                </svg>
                                <div className="absolute inset-0 flex flex-col items-center justify-center">
                                    <span className="text-5xl font-bold text-[#1E5245]">{stats.ecoScore}</span>
                                    <span className="text-xs font-bold text-gray-500 uppercase tracking-widest">Eco Score</span>
                                </div>
                            </div>
                            <h3 className="text-xl font-bold text-[#1E5245] mb-2">Sustainable Shopper</h3>
                            <p className="text-sm text-gray-500 mb-6">Your purchasing habits have reduced kitchen waste by 12.4kg this month.</p>
                            <button className="bg-[#E8F8F3] text-[#2D9B81] px-6 py-2 rounded-full text-sm font-bold hover:bg-[#D4F1E8] transition-colors">
                                View Detailed Report
                            </button>
                        </div>

                        {/* Research Insights / Methodology Section */}
                        <div className="lg:col-span-2 space-y-6">
                            <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100">
                                <div className="flex items-center justify-between mb-6">
                                    <h3 className="text-2xl font-bold text-[#1E5245]">AI Research Validation</h3>
                                    <span className="bg-blue-100 text-blue-800 text-[10px] font-bold px-3 py-1 rounded-full uppercase">Ref: IT22117946</span>
                                </div>
                                <div className="space-y-4">
                                    <div className="flex items-start space-x-4">
                                        <div className="bg-green-100 p-2 rounded-lg mt-1"><Globe size={20} className="text-green-700" /></div>
                                        <div>
                                            <h4 className="font-bold text-gray-800">Trilingual Support (SI/TA/EN)</h4>
                                            <p className="text-sm text-gray-600">Native speaker translation verification achieving inter-rater reliability of κ=0.91 for Sinhala and κ=0.89 for Tamil.</p>
                                        </div>
                                    </div>
                                    <div className="flex items-start space-x-4">
                                        <div className="bg-blue-100 p-2 rounded-lg mt-1"><Target size={20} className="text-blue-700" /></div>
                                        <div>
                                            <h4 className="font-bold text-gray-800">Hybrid AI Personalization</h4>
                                            <p className="text-sm text-gray-600">Combines LLM inference with locally trained "User Profile Models" achieving significant confidence increase (d=3.15).</p>
                                        </div>
                                    </div>
                                    <div className="flex items-start space-x-4">
                                        <div className="bg-purple-100 p-2 rounded-lg mt-1"><BarChart3 size={20} className="text-purple-700" /></div>
                                        <div>
                                            <h4 className="font-bold text-gray-800">Scalable Architecture</h4>
                                            <p className="text-sm text-gray-600">Optimized queries achieving 95% speed improvement to 94ms using float32-to-int8 quantization.</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-gradient-to-br from-[#1E5245] to-[#2D9B81] p-8 rounded-3xl shadow-xl text-white relative overflow-hidden">
                                <div className="relative z-10">
                                    <h3 className="text-xl font-bold mb-2 flex items-center">
                                        <Info className="mr-2" size={20} /> Sustainable Goal
                                    </h3>
                                    <p className="opacity-90 mb-4 text-sm">You are on track to save 87.8 tonnes of food waste annually if scaled to 1 million households. Keep up the sustainable purchasing!</p>
                                    <div className="w-full bg-white/20 h-2 rounded-full overflow-hidden">
                                        <div className="bg-white h-full w-[74%]"></div>
                                    </div>
                                    <div className="flex justify-between mt-2 text-[10px] font-bold uppercase tracking-wider">
                                        <span>Current Impact</span>
                                        <span>Goal: Zero Waste</span>
                                    </div>
                                </div>
                                <div className="absolute bottom-0 right-0 -mb-10 -mr-10 opacity-10">
                                    <TrendingDown size={200} />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <ChatAssistant />
        </div>
    );
}
