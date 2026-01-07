import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  SearchIcon,
  BrainIcon,
  MessageCircleIcon,
  ClockIcon,
  ArrowRightIcon
} from 'lucide-react';
import { Sidebar } from '../components/Sidebar';
import { ChatAssistant } from '../components/ChatAssistant';
import { MealForecast } from '../components/MealForecast';

export function Home() {
  const navigate = useNavigate();
  const features = [
    {
      icon: SearchIcon,
      title: 'Voice & Text Search',
      description: 'Search products naturally using your voice or keyboard'
    },
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#D4F1E8] via-[#E8F8F3] to-[#C8E6E0]">
      <Sidebar />
      <div className="ml-64 min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center mb-16">
            <h1 className="text-5xl md:text-6xl font-bold text-[#1E5245] mb-6">
              Shop Smarter with Your
              <span className="text-[#2D9B81]"> AI Shopping Agent</span>
            </h1>
            <p className="text-xl text-[#2D5F4F] mb-8 max-w-3xl mx-auto">
              Search products by voice or text and get intelligent
              recommendations powered by advanced AI technology
            </p>
            <button
              onClick={() => navigate('/smart-shopping/search')}
              className="inline-flex items-center space-x-2 bg-[#2D9B81] text-white px-8 py-4 rounded-full text-lg font-semibold hover:bg-[#267A68] transition-all hover:scale-105 shadow-lg"
            >
              <span>Start Now</span>
              <ArrowRightIcon size={20} />
            </button>
          </div>

          <MealForecast />

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
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

