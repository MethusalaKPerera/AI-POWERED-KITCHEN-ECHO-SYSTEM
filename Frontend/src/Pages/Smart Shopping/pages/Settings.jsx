import React, { useState } from 'react';
import { GlobeIcon, DollarSignIcon, BrainIcon, TrashIcon } from 'lucide-react';
import { Sidebar } from '../components/Sidebar';
import { ChatAssistant } from '../components/ChatAssistant';
import { useLanguage } from '../context/LanguageContext';
import { useCurrency } from '../context/CurrencyContext';
import { useHistory } from '../context/HistoryContext';

export function Settings() {
  const { language, setLanguage } = useLanguage();
  const { currency, setCurrency } = useCurrency();
  const { clearHistory } = useHistory();
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [saveHistory, setSaveHistory] = useState(true);

  return (
    <div className="min-h-screen bg-[#E8F8F3]">
      <Sidebar />
      <div className="ml-64 min-h-screen">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-[#1E5245] mb-2">Settings</h1>
            <p className="text-[#2D5F4F]">
              Manage your preferences and account settings
            </p>
          </div>
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center space-x-3 mb-4">
                <GlobeIcon className="text-[#2D9B81]" size={24} />
                <h2 className="text-xl font-semibold text-[#1E5245]">
                  Language
                </h2>
              </div>
              <p className="text-[#2D5F4F] mb-4">
                Choose your preferred language
              </p>
              <select
                value={language}
                onChange={e => setLanguage(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#2D9B81]"
              >
                <option value="en">English</option>
                <option value="si">සිංහල (Sinhala)</option>
                <option value="ta">தமிழ் (Tamil)</option>
              </select>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center space-x-3 mb-4">
                <DollarSignIcon className="text-[#2D9B81]" size={24} />
                <h2 className="text-xl font-semibold text-[#1E5245]">
                  Currency
                </h2>
              </div>
              <p className="text-[#2D5F4F] mb-4">
                Select your preferred currency
              </p>
              <select
                value={currency}
                onChange={e => setCurrency(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#2D9B81]"
              >
                <option value="USD">USD - US Dollar ($)</option>
                <option value="EUR">EUR - Euro (€)</option>
                <option value="LKR">LKR - Sri Lankan Rupee (Rs)</option>
                <option value="INR">INR - Indian Rupee (₹)</option>
                <option value="GBP">GBP - British Pound (£)</option>
              </select>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center space-x-3 mb-4">
                <BrainIcon className="text-[#2D9B81]" size={24} />
                <h2 className="text-xl font-semibold text-[#1E5245]">
                  AI Preferences
                </h2>
              </div>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-[#1E5245]">
                      Enable Voice Input
                    </p>
                    <p className="text-sm text-[#2D5F4F]">
                      Use voice commands for searching
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={voiceEnabled}
                      onChange={e => setVoiceEnabled(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-[#D4F1E8] rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#2D9B81]"></div>
                  </label>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-[#1E5245]">
                      Save Search History
                    </p>
                    <p className="text-sm text-[#2D5F4F]">
                      Store your searches for future reference
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={saveHistory}
                      onChange={e => setSaveHistory(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-[#D4F1E8] rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#2D9B81]"></div>
                  </label>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center space-x-3 mb-4">
                <TrashIcon className="text-red-600" size={24} />
                <h2 className="text-xl font-semibold text-[#1E5245]">
                  Data Management
                </h2>
              </div>
              <p className="text-[#2D5F4F] mb-4">
                Clear all stored data and reset preferences
              </p>
              <button
                onClick={() => {
                  if (window.confirm('Are you sure you want to clear all data?')) {
                    clearHistory();
                    alert('All data has been cleared');
                  }
                }}
                className="px-6 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
              >
                Reset All Data
              </button>
            </div>
          </div>
        </div>
      </div>
      <ChatAssistant />
    </div>
  );
}

