import React, { useState } from 'react';
import { MessageCircleIcon, SendIcon, XIcon } from 'lucide-react';

export function ChatAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([{
    id: '1',
    text: "Hi! I'm your AI Shopping Assistant. How can I help you find the perfect product today?",
    isUser: false,
    timestamp: new Date()
  }]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      text: input,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Call Gemini API through backend
      const response = await fetch('http://localhost:5000/api/shopping/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          context: 'shopping assistant'
        })
      });

      const data = await response.json();

      const aiResponse = {
        id: (Date.now() + 1).toString(),
        text: data.response || 'I can help you with that! Let me find the best options for you.',
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorResponse = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error. Please try again.',
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 bg-[#2D9B81] text-white p-4 rounded-full shadow-lg hover:bg-[#267A68] transition-all hover:scale-110 z-50"
        >
          <MessageCircleIcon size={28} />
        </button>
      )}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[500px] bg-white rounded-lg shadow-2xl flex flex-col z-50">
          <div className="bg-[#2D9B81] text-white p-4 rounded-t-lg flex justify-between items-center">
            <h3 className="font-semibold">AI Shopping Assistant</h3>
            <button
              onClick={() => setIsOpen(false)}
              className="hover:bg-[#267A68] rounded p-1"
            >
              <XIcon size={20} />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map(message => (
              <div
                key={message.id}
                className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-3 rounded-lg ${message.isUser
                    ? 'bg-[#2D9B81] text-white rounded-br-none'
                    : 'bg-gray-100 text-gray-800 rounded-bl-none'
                    }`}
                >
                  <p className="text-sm">{message.text}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="p-4 border-t">
            <div className="flex space-x-2">
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyPress={e => e.key === 'Enter' && handleSend()}
                placeholder="Type your message..."
                className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#2D9B81]"
              />
              <button
                onClick={handleSend}
                className="bg-[#2D9B81] text-white p-2 rounded-lg hover:bg-[#267A68] transition-colors"
              >
                <SendIcon size={20} />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

