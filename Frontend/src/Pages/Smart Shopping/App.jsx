import React from 'react';
import { AppRouter } from './AppRouter';
import { LanguageProvider } from './context/LanguageContext';
import { CurrencyProvider } from './context/CurrencyContext';
import { HistoryProvider } from './context/HistoryContext';

export function App() {
  return (
    <LanguageProvider>
      <CurrencyProvider>
        <HistoryProvider>
          <div className="w-full min-h-screen bg-gray-50">
            <AppRouter />
          </div>
        </HistoryProvider>
      </CurrencyProvider>
    </LanguageProvider>
  );
}

