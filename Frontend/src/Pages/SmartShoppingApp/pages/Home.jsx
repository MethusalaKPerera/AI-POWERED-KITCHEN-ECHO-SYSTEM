import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BrainIcon,
  MessageCircleIcon,
  ClockIcon,
  ArrowRightIcon,
  Loader2
} from 'lucide-react';
import { Sidebar } from '../components/Sidebar';
import { ChatAssistant } from '../components/ChatAssistant';
import { MealForecast } from '../components/MealForecast';

export function Home() {
  const navigate = useNavigate();
  const [showAnalyzing, setShowAnalyzing] = useState(true);
  const features = [
    {
      icon: BrainIcon,
      title: 'Smart Recommendations',
      description: 'AI-powered suggestions tailored to your preferences'
    },
    {
      icon: MessageCircleIcon,
      title: 'AI Assistant Help',
      description: 'Get instant guidance from our intelligent chatbot'
    },
    {
      icon: ClockIcon,
      title: 'Search History',
      description: 'Manage and revisit your previous searches easily'
    }
  ];

  useEffect(() => {
    const t = setTimeout(() => setShowAnalyzing(false), 4000);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="min-h-screen bg-[#E8F8F3]">
      <Sidebar />
      <div className="ml-[17rem] min-h-screen pl-8 pr-6 pt-6 overflow-x-hidden">
        <div className="max-w-5xl mx-auto min-w-0">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-[#1E5245] mb-4 leading-tight">
              Shop Smarter with Your <span className="text-[#2D9B81]">AI Shopping Agent</span>
            </h1>
            <p className="text-lg text-[#2D5F4F] mb-6 max-w-2xl mx-auto">
              Search products by voice or text and get intelligent recommendations powered by advanced AI technology.
            </p>
            <button
              onClick={() => navigate('/smart-shopping/search')}
              className="inline-flex items-center space-x-2 bg-[#2D9B81] text-white px-8 py-4 rounded-xl text-lg font-semibold hover:bg-[#267A68] transition-all shadow-lg"
            >
              <span>Start Now</span>
              <ArrowRightIcon size={20} />
            </button>
            {showAnalyzing && (
              <div className="mt-4 flex items-center justify-center gap-2 text-[#2D5F4F]">
                <Loader2 className="h-5 w-5 animate-spin" />
                <span className="text-sm font-medium">AI is analyzing your taste...</span>
              </div>
            )}
          </div>

          <MealForecast />

          <div className="grid md:grid-cols-3 gap-8 mb-16">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={index}
                  className="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition-shadow"
                >
                  <div className="bg-[#D4F1E8] w-14 h-14 rounded-full flex items-center justify-center mb-4">
                    <Icon className="text-[#2D9B81]" size={28} />
                  </div>
                  <h3 className="text-xl font-semibold text-[#1E5245] mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-[#2D5F4F]">{feature.description}</p>
                </div>
              );
            })}
          </div>
          <div className="bg-gradient-to-r from-[#2D9B81] to-[#25866F] rounded-2xl p-12 text-center text-white shadow-xl">
            <h2 className="text-3xl font-bold mb-4">
              Ready to Transform Your Shopping Experience?
            </h2>
            <p className="text-lg mb-6 opacity-90">
              Join thousands of smart shoppers using AI to find the best
              products
            </p>
            <button
              onClick={() => navigate('/smart-shopping/search')}
              className="bg-white text-[#2D9B81] px-8 py-3 rounded-full font-semibold hover:bg-gray-100 transition-colors"
            >
              Get Started Free
            </button>
          </div>
        </div>
      </div>
      <ChatAssistant />
    </div>
  );
}

