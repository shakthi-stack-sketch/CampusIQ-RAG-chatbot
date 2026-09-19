import React, { useState, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ChatArea from './components/ChatArea';
import VoiceRecorderModal from './components/VoiceRecorderModal';
import { 
  getConversations, 
  getConversation, 
  createConversation, 
  sendMessage, 
  renameConversation, 
  deleteConversation 
} from './services/api';

export default function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem('campusiq_theme') || 'light');
  const [conversations, setConversations] = useState({ today: [], yesterday: [], earlier: [] });
  const [activeConvId, setActiveConvId] = useState(null);
  const [activeConv, setActiveConv] = useState(null);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [voiceModalOpen, setVoiceModalOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);

  const activeConvIdRef = useRef(activeConvId);
  useEffect(() => {
    activeConvIdRef.current = activeConvId;
  }, [activeConvId]);

  // Sync theme attribute on document root
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('campusiq_theme', theme);
  }, [theme]);

  // Load conversations on mount or search
  useEffect(() => {
    loadConversationList(searchQuery);
  }, [searchQuery]);

  const loadConversationList = async (query = '') => {
    try {
      const data = await getConversations(query);
      setConversations(data);
    } catch (e) {
      console.warn('Failed to load conversations:', e);
    }
  };

  const handleSelectConversation = async (convId) => {
    try {
      setActiveConvId(convId);
      activeConvIdRef.current = convId;
      const data = await getConversation(convId);
      setActiveConv(data);
    } catch (e) {
      console.error('Failed to load conversation details:', e);
    }
  };

  const handleNewChat = () => {
    setActiveConvId(null);
    activeConvIdRef.current = null;
    setActiveConv(null);
    setSelectedCategory(null);
    setInputMessage('');
  };

  const handleSendMessage = async (userText) => {
    if (!userText || !userText.trim() || isLoading) return;

    const trimmedText = userText.trim();
    const tempUserMsg = {
      id: `temp_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
      role: 'user',
      content: trimmedText,
      created_at: new Date().toISOString()
    };

    const currentConvId = activeConvIdRef.current || activeConvId || activeConv?.id || null;

    // Optimistically update UI by appending the new user message
    setActiveConv((prev) => ({
      id: prev?.id || currentConvId || 'pending',
      title: prev?.title || 'Campus Inquiry',
      messages: [...(prev?.messages || []), tempUserMsg]
    }));

    setIsLoading(true);

    try {
      const res = await sendMessage({
        conversation_id: currentConvId,
        message: trimmedText,
        category_filter: selectedCategory
      });

      const assistantMsg = {
        id: res.assistant_message_id,
        role: 'assistant',
        content: res.answer,
        sources: res.sources || [],
        created_at: new Date().toISOString()
      };

      const finalConvId = res.conversation_id;
      activeConvIdRef.current = finalConvId;
      setActiveConvId(finalConvId);

      setActiveConv((prev) => {
        // Replace the temporary message with confirmed user message, and append assistant message
        const existing = (prev?.messages || []).filter(m => m.id !== tempUserMsg.id);
        return {
          id: finalConvId,
          title: res.title || prev?.title || 'Campus Inquiry',
          messages: [
            ...existing,
            { ...tempUserMsg, id: res.user_message_id },
            assistantMsg
          ]
        };
      });

      // Refresh list to show updated title and timestamp
      await loadConversationList(searchQuery);
    } catch (err) {
      const errorMsg = {
        id: `err_${Date.now()}`,
        role: 'assistant',
        content: 'Analysis could not be completed at this moment. Please check your network connection and try again.',
        sources: [],
        created_at: new Date().toISOString()
      };
      setActiveConv((prev) => ({
        ...prev,
        messages: [...(prev?.messages || []), errorMsg]
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleRename = async (convId, newTitle) => {
    try {
      await renameConversation(convId, newTitle);
      if (activeConvId === convId) {
        setActiveConv((prev) => prev ? { ...prev, title: newTitle } : null);
      }
      await loadConversationList(searchQuery);
    } catch (e) {
      console.warn('Rename error:', e);
    }
  };

  const handleDelete = async (convId) => {
    try {
      await deleteConversation(convId);
      if (activeConvId === convId) {
        handleNewChat();
      }
      await loadConversationList(searchQuery);
    } catch (e) {
      console.warn('Delete error:', e);
    }
  };

  const handleApplyVoiceTranscript = (transcriptText) => {
    // Populate the chat input with the recognized text for review/editing/Enter submission
    if (transcriptText && transcriptText.trim()) {
      setInputMessage(transcriptText.trim());
      // Auto focus the input textarea so user can press ENTER immediately
      setTimeout(() => {
        const textarea = document.querySelector('textarea');
        if (textarea) {
          textarea.focus();
        }
      }, 50);
    }
  };

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      {/* Left Sidebar */}
      <Sidebar
        conversations={conversations}
        activeConvId={activeConvId}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        onRenameConversation={handleRename}
        onDeleteConversation={handleDelete}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        theme={theme}
        onToggleTheme={toggleTheme}
      />

      {/* Main Content Area */}
      <main style={{
        display: 'flex',
        flexDirection: 'column',
        flex: 1,
        height: '100%',
        minHeight: 0,
        minWidth: 0,
        overflow: 'hidden',
        position: 'relative'
      }}>
        <Header
          activeConvTitle={activeConv?.title}
          hasMessages={Boolean(activeConv?.messages && activeConv.messages.length > 0)}
        />

        <ChatArea
          messages={activeConv?.messages || []}
          isLoading={isLoading}
          inputMessage={inputMessage}
          setInputMessage={setInputMessage}
          onSendMessage={handleSendMessage}
          onOpenVoiceRecorder={() => setVoiceModalOpen(true)}
          selectedCategory={selectedCategory}
          onSelectCategory={(cat) => setSelectedCategory(cat)}
          onClearCategory={() => setSelectedCategory(null)}
        />
      </main>

      {/* Voice Recording Modal */}
      <VoiceRecorderModal
        isOpen={voiceModalOpen}
        onClose={() => setVoiceModalOpen(false)}
        onApplyTranscript={handleApplyVoiceTranscript}
      />
    </div>
  );
}

