import { useState, useEffect } from 'react';
import Head from 'next/head';
import ChatBox from '../components/ChatBox';
import { Message } from '../types';

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Welcome to the Defense Analyst Chatbot. How can I assist with your defense research today?',
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const addMessage = (message: Message) => {
    setMessages((prev) => [...prev, message]);
  };

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;
    
    // Add user message to the chat
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: content,
    };
    addMessage(userMessage);
    
    // Set loading state
    setIsLoading(true);
    
    try {
      // Call the API to get a response
      const response = await fetch(`${process.env.BACKEND_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: content,
          conversation_id: conversationId,
          include_research_data: true,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Update conversation ID
      setConversationId(data.conversation_id);
      
      // Add bot response to chat
      const botMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: data.response,
        researchData: data.research_data,
        sources: data.sources,
      };
      addMessage(botMessage);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      addMessage({
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Head>
        <title>Defense Analyst Chatbot</title>
        <meta name="description" content="A chatbot specialized in defense research and analysis" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="container mx-auto px-4 py-8 max-w-4xl">
        <h1 className="text-3xl font-bold text-center mb-8 text-blue-800">
          Defense Analyst Chatbot
        </h1>
        
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <ChatBox 
            messages={messages} 
            onSendMessage={handleSendMessage} 
            isLoading={isLoading} 
          />
        </div>
      </main>

      <footer className="text-center py-4 text-gray-600 text-sm">
        Defense Analyst Chatbot &copy; {new Date().getFullYear()}
      </footer>
    </div>
  );
}
