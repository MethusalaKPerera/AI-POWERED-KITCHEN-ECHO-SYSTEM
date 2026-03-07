import React from 'react';
import { AppRouter } from './AppRouter';
import { LanguageProvider } from './context/LanguageContext';
import { CurrencyProvider } from './context/CurrencyContext';
import { HistoryProvider } from './context/HistoryContext';
import { ChatProvider } from './context/ChatContext';

export function App() {
  return (
    <LanguageProvider>
      <CurrencyProvider>
        <HistoryProvider>
          <ChatProvider>
            <div className="w-full min-h-screen bg-transparent">
              <AppRouter />
            </div>
          </ChatProvider>
        </HistoryProvider>
      </CurrencyProvider>
    </LanguageProvider>
  );
}

