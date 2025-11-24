import React, { useState, createContext, useContext } from 'react';

const currencySymbols = {
  USD: '$',
  EUR: '€',
  LKR: 'Rs',
  INR: '₹',
  GBP: '£'
};

const CurrencyContext = createContext(undefined);

export function CurrencyProvider({ children }) {
  const [currency, setCurrency] = useState('USD');

  const convertPrice = (price) => {
    return `${currencySymbols[currency]}${price.toFixed(2)}`;
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

