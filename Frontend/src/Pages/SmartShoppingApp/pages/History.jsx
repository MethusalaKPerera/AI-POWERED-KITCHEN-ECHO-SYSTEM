import React, { useState } from 'react';
import { SearchIcon, TrashIcon, EditIcon, PlayIcon } from 'lucide-react';
import { Sidebar } from '../components/Sidebar';
import { ChatAssistant } from '../components/ChatAssistant';
import { useHistory } from '../context/HistoryContext';

export function History() {
  const { history, deleteFromHistory, updateHistory, clearHistory, setHistory } = useHistory();
  const [searchTerm, setSearchTerm] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [loading, setLoading] = useState(false);

  // Fetch history from backend on mount
  React.useEffect(() => {
    const fetchHistory = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('token');
        if (token) {
          // We need to define shoppingApi properly or use direct fetch
          // Assuming shoppingApi is available via props or context or import
          // But for now let's use the one imported in Search.jsx pattern
          const response = await fetch('/api/shopping/history', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          if (response.ok) {
            const data = await response.json();
            if (setHistory) setHistory(data);
          }
        }
      } catch (error) {
        console.error("Failed to fetch history", error);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, [setHistory]);

  const filteredHistory = history.filter(item =>
    item.query.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleEdit = (id, currentQuery) => {
    setEditingId(id);
    setEditValue(currentQuery);
  };

  const handleSaveEdit = (id) => {
    updateHistory(id, editValue);
    setEditingId(null);
  };

  return (
    <div className="min-h-screen bg-[#E8F8F3]">
      <Sidebar />
      <div className="ml-64 min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-[#1E5245] mb-2">
              Search History
            </h1>
            <p className="text-[#2D5F4F]">
              View, edit, or re-run your previous searches
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex items-center space-x-4 mb-4">
              <div className="flex-1 relative">
                <SearchIcon
                  className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                  size={20}
                />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  placeholder="Search history..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#2D9B81]"
                />
              </div>
              <button
                onClick={clearHistory}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
              >
                Clear All
              </button>
            </div>
            {filteredHistory.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">No search history found</p>
              </div>
            ) : (
              <div className="space-y-3">
                {filteredHistory.map(item => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex-1">
                      {editingId === item.id ? (
                        <input
                          type="text"
                          value={editValue}
                          onChange={e => setEditValue(e.target.value)}
                          className="w-full px-3 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#2D9B81]"
                        />
                      ) : (
                        <>
                          <p className="text-lg font-medium text-[#1E5245]">
                            {item.query}
                          </p>
                          <p className="text-sm text-[#2D5F4F]">
                            {new Date(item.timestamp).toLocaleDateString()} at{' '}
                            {new Date(item.timestamp).toLocaleTimeString()}
                          </p>
                        </>
                      )}
                    </div>
                    <div className="flex items-center space-x-2 ml-4">
                      {editingId === item.id ? (
                        <button
                          onClick={() => handleSaveEdit(item.id)}
                          className="px-3 py-1 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                        >
                          Save
                        </button>
                      ) : (
                        <>
                          <button
                            onClick={() => console.log('Re-run:', item.query)}
                            className="p-2 text-[#2D9B81] hover:bg-[#D4F1E8] rounded-md transition-colors"
                            title="Re-run search"
                          >
                            <PlayIcon size={18} />
                          </button>
                          <button
                            onClick={() => handleEdit(item.id, item.query)}
                            className="p-2 text-gray-600 hover:bg-gray-200 rounded-md transition-colors"
                            title="Edit"
                          >
                            <EditIcon size={18} />
                          </button>
                          <button
                            onClick={() => deleteFromHistory(item.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
                            title="Delete"
                          >
                            <TrashIcon size={18} />
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
      <ChatAssistant />
    </div>
  );
}

