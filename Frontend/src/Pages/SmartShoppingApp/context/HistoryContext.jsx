import React, { useEffect, useState, createContext, useContext } from 'react';
import { shoppingApi } from '../../../services/api';

const HistoryContext = createContext(undefined);

export function HistoryProvider({ children }) {
  const [history, setHistory] = useState([]);

  // Note: Loading is handled in History.jsx, but we could also do it here.
  // For now, let's just implement the actions.

  const addToHistory = (query, filters) => {
    // We'll let the backend search/chat routes handle this automatically.
    // If called manually, it adds to local state.
    const newItem = {
      id: Date.now().toString(),
      query,
      timestamp: new Date(),
      filters
    };
    setHistory(prev => [newItem, ...prev].slice(0, 50));
  };

  const deleteFromHistory = async (id) => {
    try {
      await shoppingApi.deleteHistory(id);
      setHistory(prev => prev.filter(item => item.id !== id));
    } catch (error) {
      console.error('Failed to delete history item:', error);
    }
  };

  const updateHistory = async (id, query) => {
    try {
      await shoppingApi.updateHistory(id, query);
      setHistory(prev =>
        prev.map(item => (item.id === id ? { ...item, query } : item))
      );
    } catch (error) {
      console.error('Failed to update history item:', error);
    }
  };

  const clearHistory = async () => {
    try {
      await shoppingApi.clearHistory();
      setHistory([]);
    } catch (error) {
      console.error('Failed to clear history:', error);
    }
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

