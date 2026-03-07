import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { SearchIcon, TrashIcon, EditIcon, PlayIcon, MessageCircleIcon } from 'lucide-react';
import { useChat } from '../context/ChatContext';
import { Sidebar } from '../components/Sidebar';
import { ChatAssistant } from '../components/ChatAssistant';
import { useHistory } from '../context/HistoryContext';
import { shoppingApi } from '../../../services/api';

export function History() {
  const navigate = useNavigate();
  const { triggerChat } = useChat();
  const { history, deleteFromHistory, updateHistory, clearHistory, setHistory } = useHistory();
  const [searchTerm, setSearchTerm] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('all'); // 'all', 'search', 'chat'

  // Fetch history from backend on mount
  React.useEffect(() => {
    const fetchHistory = async () => {
      setLoading(true);
      try {
        const data = await shoppingApi.getHistory();
        const list = Array.isArray(data) ? data : (data?.data || []);
        if (setHistory) setHistory(list);
      } catch (error) {
        console.error("Failed to fetch history", error);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, [setHistory]);

  const filteredHistory = history.filter(item => {
    const q = (item.query || item.text || '').toString();
    const matchesSearch = q.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab = activeTab === 'all' || (item.type || 'search') === activeTab;
    return matchesSearch && matchesTab;
  });

  const handleEdit = (id, currentQuery) => {
    setEditingId(id);
    setEditValue(currentQuery);
  };

  const handleSaveEdit = (id) => {
    updateHistory(id, editValue);
    setEditingId(null);
  };

  const handleReRun = (item) => {
    if (item.type === 'chat') {
      triggerChat(item.query);
    } else {
      navigate(`/smart-shopping/search?q=${encodeURIComponent(item.query)}`);
    }
  };

  return (
    <div className="min-h-screen bg-[#E8F8F3]">
      <Sidebar />
      <div className="ml-[17rem] min-h-screen pl-8 pr-6 pt-6 overflow-x-hidden">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-[#1E5245] mb-2">
              Search History
            </h1>
            <p className="text-[#2D5F4F] text-lg">
              View, edit, or re-run your previous activities.
            </p>
          </div>

          <div className="flex gap-2 mb-6">
            {[
              { id: 'all', label: 'All' },
              { id: 'search', label: 'Search' },
              { id: 'chat', label: 'Chat' }
            ].map(({ id, label }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`px-6 py-2.5 rounded-lg font-medium transition-all ${activeTab === id
                  ? 'bg-[#2D9B81] text-white shadow-md'
                  : 'bg-white text-[#2D5F4F] border border-gray-200 hover:border-[#2D9B81]/50'
                  }`}
              >
                {label}
              </button>
            ))}
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1 relative">
                <SearchIcon
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                  size={20}
                />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  placeholder="Search history..."
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2D9B81] focus:border-[#2D9B81]"
                />
              </div>
              <button
                onClick={clearHistory}
                className="px-5 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium whitespace-nowrap"
              >
                Clear All
              </button>
            </div>
            {filteredHistory.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">No search history found</p>
              </div>
            ) : (
              <div className="space-y-2">
                {filteredHistory.map(item => {
                const itemId = item.id ?? item._id;
                const queryText = (item.query ?? item.text ?? '').toString();
                const itemType = (item.type ?? 'search').toLowerCase();
                const ts = item.timestamp ? new Date(item.timestamp) : null;
                return (
                  <div
                    key={itemId}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-100 hover:bg-gray-50/90 transition-colors"
                  >
                    <div className="flex-1 flex items-center gap-4 min-w-0 overflow-hidden">
                      <div className={`flex-shrink-0 p-2 rounded-lg ${itemType === 'chat' ? 'bg-blue-100 text-blue-600' : 'bg-[#D4F1E8] text-[#2D9B81]'}`}>
                        {itemType === 'chat' ? <MessageCircleIcon size={20} /> : <SearchIcon size={20} />}
                      </div>
                      <div className="flex-1 min-w-0 overflow-hidden">
                        {editingId === itemId ? (
                          <input
                            type="text"
                            value={editValue}
                            onChange={e => setEditValue(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2D9B81]"
                          />
                        ) : (
                          <>
                            <div className="flex flex-wrap items-center gap-2">
                              <p className="text-[#1E5245] font-medium break-words overflow-visible">
                                {queryText || '—'}
                              </p>
                              <span className={`text-xs uppercase tracking-wider px-2 py-0.5 rounded font-semibold flex-shrink-0 ${itemType === 'chat' ? 'bg-blue-50 text-blue-600' : 'text-[#2D9B81] bg-[#D4F1E8]'}`}>
                                {itemType}
                              </span>
                            </div>
                            {ts && (
                              <p className="text-sm text-gray-500 mt-0.5">
                                {ts.toLocaleDateString()} at {ts.toLocaleTimeString()}
                              </p>
                            )}
                          </>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-1 ml-4 flex-shrink-0">
                      {editingId === itemId ? (
                        <button
                          onClick={() => handleSaveEdit(itemId)}
                          className="px-3 py-1 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                        >
                          Save
                        </button>
                      ) : (
                        <>
                          <button
                            onClick={() => handleReRun({ ...item, id: itemId, query: queryText, type: itemType })}
                            className="p-2 text-[#2D9B81] hover:bg-[#D4F1E8] rounded-md transition-colors"
                            title="Re-run activity"
                          >
                            <PlayIcon size={18} />
                          </button>
                          <button
                            onClick={() => handleEdit(itemId, queryText)}
                            className="p-2 text-gray-600 hover:bg-gray-200 rounded-md transition-colors"
                            title="Edit"
                          >
                            <EditIcon size={18} />
                          </button>
                          <button
                            onClick={() => deleteFromHistory(itemId)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
                            title="Delete"
                          >
                            <TrashIcon size={18} />
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                );
              })}
              </div>
            )}
          </div>
        </div>
      </div>
      <ChatAssistant />
    </div>
  );
}

