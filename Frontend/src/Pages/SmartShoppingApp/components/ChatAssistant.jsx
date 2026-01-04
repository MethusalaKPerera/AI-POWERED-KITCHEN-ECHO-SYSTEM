import React, { useState } from 'react';
import { MessageCircleIcon, SendIcon, XIcon } from 'lucide-react';
import { useChat } from '../context/ChatContext';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export function ChatAssistant() {
  const { chatRequest } = useChat();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([{
    id: '1',
    text: "Hi! I'm your AI Shopping Assistant. How can I help you find the perfect product today?",
    isUser: false,
    timestamp: new Date()
  }]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Custom styles for markdown content
  const MarkdownStyles = ({ children, isUser }) => (
    <div className={`markdown-content ${isUser ? 'prose-invert' : 'prose'}`}>
      <style>{`
        .markdown-content { font-size: 0.875rem; line-height: 1.25rem; }
        .markdown-content p { margin-bottom: 0.5rem; }
        .markdown-content p:last-child { margin-bottom: 0; }
        .markdown-content strong { font-weight: 700; color: inherit; }
        .markdown-content table { width: 100%; border-collapse: collapse; margin-top: 0.5rem; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; }
        .markdown-content th, .markdown-content td { padding: 0.5rem; border: 1px solid rgba(0,0,0,0.1); text-align: left; }
        .markdown-content th { background: rgba(0,0,0,0.05); font-weight: bold; }
        .markdown-content h1, .markdown-content h2, .markdown-content h3 { font-weight: bold; margin-top: 0.5rem; margin-bottom: 0.25rem; font-size: 1rem; }
        .markdown-content ul, .markdown-content ol { margin-left: 1.25rem; margin-bottom: 0.5rem; }
        .markdown-content li { list-style-type: disc; margin-bottom: 0.25rem; }
      `}</style>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {children}
      </ReactMarkdown>
    </div>
  );

  // Listen for external chat triggers (from History page)
  React.useEffect(() => {
    if (chatRequest?.message) {
      setIsOpen(true);
      // We use a small delay to ensure the component is ready
      const timer = setTimeout(() => {
        handleTriggerSend(chatRequest.message);
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [chatRequest]);

  const handleTriggerSend = async (message) => {
    setInput(message);
    // Directly call handleSend logic or equivalent
    // For simplicity, we'll just set the input and let the user click, 
    // OR we can copy the logic here to auto-send.
    // Let's auto-send for a better "Re-run" experience.
    await executeSend(message);
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    await executeSend(input);
  };

  const executeSend = async (textToSend) => {
    const userMessage = {
      id: Date.now().toString(),
      text: textToSend,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Call Gemini API through backend
      const token = localStorage.getItem('token');
      const headers = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch('/api/shopping/chat', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          message: textToSend,
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
                  className={`max-w-[90%] p-3 rounded-lg ${message.isUser
                    ? 'bg-[#2D9B81] text-white rounded-br-none shadow-sm'
                    : 'bg-gray-100 text-gray-800 rounded-bl-none shadow-sm'
                    }`}
                >
                  <MarkdownStyles isUser={message.isUser}>
                    {message.text}
                  </MarkdownStyles>
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

