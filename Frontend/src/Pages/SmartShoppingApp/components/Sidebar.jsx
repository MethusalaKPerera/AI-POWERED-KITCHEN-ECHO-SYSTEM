import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  SearchIcon,
  StarIcon,
  ClockIcon,
  SettingsIcon,
  GlobeIcon,
  DollarSignIcon
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { useCurrency } from '../context/CurrencyContext';

export function Sidebar() {
  const location = useLocation();
  const { language, setLanguage, translations } = useLanguage();
  const { currency, setCurrency } = useCurrency();

  const navItems = [
    { path: '/smart-shopping', icon: HomeIcon, label: translations.home },
    { path: '/smart-shopping/search', icon: SearchIcon, label: translations.search },
    { path: '/smart-shopping/recommendations', icon: StarIcon, label: translations.recommendations },
    { path: '/smart-shopping/history', icon: ClockIcon, label: translations.history },
    { path: '/smart-shopping/settings', icon: SettingsIcon, label: translations.settings }
  ];

  return (
    <div className="fixed left-0 top-0 h-screen w-64 bg-[#2D9B81] text-white flex flex-col shadow-lg z-50">
      <div className="p-6 border-b border-teal-600">
        <Link to="/smart-shopping" className="text-2xl font-bold">
          AI Shop
        </Link>
      </div>
      <nav className="flex-1 py-6">
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path ||
            (item.path === '/smart-shopping' && location.pathname === '/smart-shopping/');
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-3 px-6 py-3 transition-colors ${isActive
                ? 'bg-teal-700 border-l-4 border-white'
                : 'hover:bg-teal-700'
                }`}
            >
              <Icon size={20} />
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>
      <div className="p-6 border-t border-teal-600 space-y-4">
        <div>
          <label className="flex items-center space-x-2 text-sm mb-2">
            <GlobeIcon size={16} />
            <span>{translations.language}</span>
          </label>
          <select
            value={language}
            onChange={e => setLanguage(e.target.value)}
            className="w-full bg-teal-700 border border-teal-600 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-white"
          >
            <option value="en">English</option>
            <option value="si">සිංහල</option>
            <option value="ta">தமிழ்</option>
          </select>
        </div>
        <div>
          <label className="flex items-center space-x-2 text-sm mb-2">
            <DollarSignIcon size={16} />
            <span>{translations.currency}</span>
          </label>
          <select
            value={currency}
            onChange={e => setCurrency(e.target.value)}
            className="w-full bg-teal-700 border border-teal-600 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-white"
          >
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="LKR">LKR</option>
            <option value="INR">INR</option>
            <option value="GBP">GBP</option>
          </select>
        </div>
      </div>
    </div>
  );
}

