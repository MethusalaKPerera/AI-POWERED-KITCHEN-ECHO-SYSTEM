import React, { createContext, useContext, useState } from 'react';

const ChatContext = createContext();

export function ChatProvider({ children }) {
    const [chatRequest, setChatRequest] = useState(null);

    const triggerChat = (message) => {
        setChatRequest({ message, timestamp: Date.now() });
    };

    return (
        <ChatContext.Provider value={{ chatRequest, triggerChat }}>
            {children}
        </ChatContext.Provider>
    );
}

export const useChat = () => useContext(ChatContext);
