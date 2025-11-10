import React from "react";
import { AppRouter } from "./Smart Shopping/AppRouter";
import { LanguageProvider } from "./Smart Shopping/context/LanguageContext";
import { CurrencyProvider } from "./Smart Shopping/context/CurrencyContext";
import { HistoryProvider } from "./Smart Shopping/context/HistoryContext";

function SmartShopping() {
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

export default SmartShopping;
