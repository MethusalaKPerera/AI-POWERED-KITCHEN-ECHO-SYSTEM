import React, { useState, createContext, useContext } from 'react';

const LanguageContext = createContext(undefined);

const translations = {
  en: {
    home: 'Home',
    search: 'Search',
    recommendations: 'Recommendations',
    history: 'History',
    settings: 'Settings',
    shopSmarter: 'Shop Smarter with Your AI Shopping Agent',
    getStarted: 'Get Started'
  },
  si: {
    home: 'මුල් පිටුව',
    search: 'සොයන්න',
    recommendations: 'නිර්දේශ',
    history: 'ඉතිහාසය',
    settings: 'සැකසුම්',
    shopSmarter: 'ඔබේ AI Shopping Agent සමඟ දක්ෂව සාප්පු යන්න',
    getStarted: 'ආරම්භ කරන්න'
  },
  ta: {
    home: 'முகப்பு',
    search: 'தேடல்',
    recommendations: 'பரிந்துரைகள்',
    history: 'வரலாறு',
    settings: 'அமைப்புகள்',
    shopSmarter: 'உங்கள் AI Shopping Agent உடன் சிறப்பாக வாங்குங்கள்',
    getStarted: 'தொடங்கு'
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

