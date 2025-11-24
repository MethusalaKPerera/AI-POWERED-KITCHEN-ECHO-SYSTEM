import React, { useState } from 'react';
import { SearchIcon, MicIcon } from 'lucide-react';

export function SearchBar({ onSearch, placeholder = 'Search for products...' }) {
  const [query, setQuery] = useState('');
  const [isListening, setIsListening] = useState(false);

  const handleSearch = () => {
    if (query.trim()) {
      onSearch(query);
    }
  };

  const handleVoiceSearch = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Voice search is not supported in your browser');
      return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => {
      setIsListening(false);
      alert('Voice recognition error occurred');
    };
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setQuery(transcript);
      onSearch(transcript);
    };
    recognition.start();
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="flex items-center bg-white rounded-full shadow-lg border border-gray-200 overflow-hidden">
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && handleSearch()}
          placeholder={placeholder}
          className="flex-1 px-6 py-4 text-lg focus:outline-none"
        />
        <button
          onClick={handleVoiceSearch}
          className={`px-4 py-4 transition-colors ${
            isListening ? 'bg-red-500 text-white' : 'text-gray-600 hover:text-[#2D9B81]'
          }`}
          title="Voice search"
        >
          <MicIcon size={24} />
        </button>
        <button
          onClick={handleSearch}
          className="px-6 py-4 bg-[#2D9B81] text-white hover:bg-[#267A68] transition-colors"
        >
          <SearchIcon size={24} />
        </button>
      </div>
    </div>
  );
}

