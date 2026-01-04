import React, { useState, createContext, useContext } from 'react';

const currencySymbols = {
  USD: '$',
  EUR: '€',
  LKR: 'Rs',
  INR: '₹',
  GBP: '£'
};

// Exchange rates relative to USD
const exchangeRates = {
  USD: 1,
  EUR: 0.92,
  LKR: 325,
  INR: 83,
  GBP: 0.79
};

const CurrencyContext = createContext(undefined);

export function CurrencyProvider({ children }) {
  const [currency, setCurrency] = useState('USD');

  const convertPrice = (priceInUSD) => {
    const convertedPrice = priceInUSD * exchangeRates[currency];
    return `${currencySymbols[currency]}${convertedPrice.toFixed(2)}`;
  };

  return (
    <CurrencyContext.Provider
      value={{
        currency,
        setCurrency,
        currencySymbol: currencySymbols[currency],
        convertPrice
      }}
    >
      {children}
    </CurrencyContext.Provider>
  );
}

export function useCurrency() {
  const context = useContext(CurrencyContext);
  if (!context) throw new Error('useCurrency must be used within CurrencyProvider');
  return context;
}

