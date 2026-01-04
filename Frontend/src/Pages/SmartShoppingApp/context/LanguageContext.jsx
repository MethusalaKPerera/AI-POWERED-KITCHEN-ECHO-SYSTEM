import React, { useState, createContext, useContext } from 'react';

const LanguageContext = createContext(undefined);

const translations = {
  en: {
    // Sidebar
    home: 'Home',
    search: 'Search',
    recommendations: 'Recommendations',
    history: 'History',
    settings: 'Settings',
    language: 'Language',
    currency: 'Currency',

    // Home page
    shopSmarter: 'Shop Smarter with Your AI Shopping Agent',
    getStarted: 'Get Started',
    aiShoppingAssistant: 'AI Shopping Assistant',

    // Search page
    searchProducts: 'Search Products',
    filters: 'Filters',
    clearAll: 'Clear all',
    priceRange: 'Price Range',
    customerReview: 'Customer Review',
    categories: 'Categories',
    inStockOnly: 'In Stock Only',
    freeShipping: 'Free Shipping',
    onSale: 'On Sale',
    sortBy: 'Sort by',
    relevance: 'Relevance',
    priceLowToHigh: 'Price: Low to High',
    priceHighToLow: 'Price: High to Low',
    rating: 'Rating',
    resultsFor: 'Results for',
    items: 'items',
    save: 'Save',

    // Settings page
    settingsTitle: 'Settings',
    managePreferences: 'Manage your preferences and account settings',
    languageTitle: 'Language',
    chooseLanguage: 'Choose your preferred language',
    currencyTitle: 'Currency',
    selectCurrency: 'Select your preferred currency',
    aiPreferences: 'AI Preferences',
    enableVoice: 'Enable Voice Input',
    useVoiceCommands: 'Use voice commands for searching',
    saveSearchHistory: 'Save Search History',
    storeSearches: 'Store your searches for future reference',
    dataManagement: 'Data Management',
    clearAllData: 'Clear all stored data and reset preferences',
    resetAllData: 'Reset All Data',
    confirmClear: 'Are you sure you want to clear all data?',
    dataCleared: 'All data has been cleared'
  },
  si: {
    // Sidebar
    home: 'මුල් පිටුව',
    search: 'සොයන්න',
    recommendations: 'නිර්දේශ',
    history: 'ඉතිහාසය',
    settings: 'සැකසුම්',
    language: 'භාෂාව',
    currency: 'මුදල්',

    // Home page
    shopSmarter: 'ඔබේ AI Shopping Agent සමඟ දක්ෂව සාප්පු යන්න',
    getStarted: 'ආරම්භ කරන්න',
    aiShoppingAssistant: 'AI සාප්පු සහායක',

    // Search page
    searchProducts: 'නිෂ්පාදන සොයන්න',
    filters: 'පෙරහන්',
    clearAll: 'සියල්ල මකන්න',
    priceRange: 'මිල පරාසය',
    customerReview: 'පාරිභෝගික සමාලෝචන',
    categories: 'වර්ග',
    inStockOnly: 'තොගයේ ඇති පමණක්',
    freeShipping: 'නොමිලේ බෙදාහැරීම',
    onSale: 'විකිණීමේදී',
    sortBy: 'අනුව වර්ග කරන්න',
    relevance: 'අදාළත්වය',
    priceLowToHigh: 'මිල: අඩු සිට ඉහළ',
    priceHighToLow: 'මිල: ඉහළ සිට අඩු',
    rating: 'ශ්‍රේණිගත කිරීම',
    resultsFor: 'සඳහා ප්‍රතිඵල',
    items: 'අයිතම',
    save: 'සුරකින්න',

    // Settings page
    settingsTitle: 'සැකසුම්',
    managePreferences: 'ඔබේ මනාපයන් සහ ගිණුම් සැකසුම් කළමනාකරණය කරන්න',
    languageTitle: 'භාෂාව',
    chooseLanguage: 'ඔබේ කැමති භාෂාව තෝරන්න',
    currencyTitle: 'මුදල්',
    selectCurrency: 'ඔබේ කැමති මුදල් තෝරන්න',
    aiPreferences: 'AI මනාපයන්',
    enableVoice: 'හඬ ආදානය සක්‍රීය කරන්න',
    useVoiceCommands: 'සෙවීම සඳහා හඬ විධාන භාවිතා කරන්න',
    saveSearchHistory: 'සෙවුම් ඉතිහාසය සුරකින්න',
    storeSearches: 'අනාගත යොමුව සඳහා ඔබේ සෙවුම් ගබඩා කරන්න',
    dataManagement: 'දත්ත කළමනාකරණය',
    clearAllData: 'සියලු ගබඩා කළ දත්ත මකා සැකසුම් නැවත සකසන්න',
    resetAllData: 'සියලු දත්ත නැවත සකසන්න',
    confirmClear: 'ඔබට සියලු දත්ත මකා දැමීමට අවශ්‍ය බව විශ්වාසද?',
    dataCleared: 'සියලු දත්ත මකා දමා ඇත'
  },
  ta: {
    // Sidebar
    home: 'முகப்பு',
    search: 'தேடல்',
    recommendations: 'பரிந்துரைகள்',
    history: 'வரலாறு',
    settings: 'அமைப்புகள்',
    language: 'மொழி',
    currency: 'நாணயம்',

    // Home page
    shopSmarter: 'உங்கள் AI Shopping Agent உடன் சிறப்பாக வாங்குங்கள்',
    getStarted: 'தொடங்கு',
    aiShoppingAssistant: 'AI வாங்குதல் உதவியாளர்',

    // Search page
    searchProducts: 'தயாரிப்புகளைத் தேடுங்கள்',
    filters: 'வடிகட்டிகள்',
    clearAll: 'அனைத்தையும் அழி',
    priceRange: 'விலை வரம்பு',
    customerReview: 'வாடிக்கையாளர் மதிப்பாய்வு',
    categories: 'வகைகள்',
    inStockOnly: 'கையிருப்பில் உள்ளவை மட்டும்',
    freeShipping: 'இலவச அனுப்புதல்',
    onSale: 'விற்பனையில்',
    sortBy: 'வரிசைப்படுத்து',
    relevance: 'தொடர்பு',
    priceLowToHigh: 'விலை: குறைவு முதல் அதிகம்',
    priceHighToLow: 'விலை: அதிகம் முதல் குறைவு',
    rating: 'மதிப்பீடு',
    resultsFor: 'க்கான முடிவுகள்',
    items: 'பொருட்கள்',
    save: 'சேமி',

    // Settings page
    settingsTitle: 'அமைப்புகள்',
    managePreferences: 'உங்கள் விருப்பத்தேர்வுகள் மற்றும் கணக்கு அமைப்புகளை நிர்வகிக்கவும்',
    languageTitle: 'மொழி',
    chooseLanguage: 'உங்கள் விருப்பமான மொழியைத் தேர்ந்தெடுக்கவும்',
    currencyTitle: 'நாணயம்',
    selectCurrency: 'உங்கள் விருப்பமான நாணயத்தைத் தேர்ந்தெடுக்கவும்',
    aiPreferences: 'AI விருப்பத்தேர்வுகள்',
    enableVoice: 'குரல் உள்ளீட்டை இயக்கு',
    useVoiceCommands: 'தேடலுக்கு குரல் கட்டளைகளைப் பயன்படுத்தவும்',
    saveSearchHistory: 'தேடல் வரலாற்றைச் சேமிக்கவும்',
    storeSearches: 'எதிர்கால குறிப்புக்காக உங்கள் தேடல்களைச் சேமிக்கவும்',
    dataManagement: 'தரவு மேலாண்மை',
    clearAllData: 'சேமிக்கப்பட்ட அனைத்து தரவையும் அழித்து விருப்பத்தேர்வுகளை மீட்டமைக்கவும்',
    resetAllData: 'அனைத்து தரவையும் மீட்டமை',
    confirmClear: 'அனைத்து தரவையும் அழிக்க விரும்புகிறீர்களா?',
    dataCleared: 'அனைத்து தரவும் அழிக்கப்பட்டது'
  }
};

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState('en');

  return (
    <LanguageContext.Provider
      value={{
        language,
        setLanguage,
        translations: translations[language]
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) throw new Error('useLanguage must be used within LanguageProvider');
  return context;
}

