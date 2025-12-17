import React, { useEffect, useState, createContext, useContext } from 'react';

const HistoryContext = createContext(undefined);

export function HistoryProvider({ children }) {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const saved = localStorage.getItem('searchHistory');
    if (saved) {
      const parsed = JSON.parse(saved);
      setHistory(
        parsed.map(item => ({
          ...item,
          timestamp: new Date(item.timestamp)
        }))
      );
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('searchHistory', JSON.stringify(history));
  }, [history]);

  const addToHistory = (query, filters) => {
    const newItem = {
      id: Date.now().toString(),
      query,
      timestamp: new Date(),
      filters
    };
    setHistory(prev => [newItem, ...prev].slice(0, 50));
  };

  const deleteFromHistory = (id) => {
    setHistory(prev => prev.filter(item => item.id !== id));
  };

  const updateHistory = (id, query) => {
    setHistory(prev =>
      prev.map(item => (item.id === id ? { ...item, query } : item))
    );
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem('searchHistory');
  };

  return (
    <HistoryContext.Provider
      value={{
        history,
        addToHistory,
        deleteFromHistory,
        updateHistory,
        clearHistory,
        setHistory
      }}
    >
      {children}
    </HistoryContext.Provider>
  );
}

export function useHistory() {
  const context = useContext(HistoryContext);
  if (!context) throw new Error('useHistory must be used within HistoryProvider');
  return context;
}

