import React, { useState, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ChatArea from './components/ChatArea';
import VoiceRecorderModal from './components/VoiceRecorderModal';
import MyCampusModal from './components/MyCampusModal';
import CampusPulseModal from './components/CampusPulseModal';
import OpportunitiesModal from './components/OpportunitiesModal';
import WhereToGoModal from './components/WhereToGoModal';
import SavedAnswersModal from './components/SavedAnswersModal';
import PersonalVaultModal from './components/PersonalVaultModal';
import AuthModal from './components/AuthModal';
import GuestPromptModal from './components/GuestPromptModal';

import { 
  getConversations, 
  getConversation, 
  sendMessage, 
  renameConversation, 
  deleteConversation,
  getSavedAnswers,
  saveAnswerApi,
  unsaveByMessageIdApi,
  getMe,
  getStoredUser,
  logoutUser,
  updateUserProfile
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

  // Authentication States
  const [currentUser, setCurrentUser] = useState(() => getStoredUser());
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authModalInitialMode, setAuthModalInitialMode] = useState('login');
  const [guestPromptOpen, setGuestPromptOpen] = useState(false);
  const [guestPromptFeature, setGuestPromptFeature] = useState('this feature');

  // Modals
  const [myCampusOpen, setMyCampusOpen] = useState(false);
  const [pulseOpen, setPulseOpen] = useState(false);
  const [opportunitiesOpen, setOpportunitiesOpen] = useState(false);
  const [whereToGoOpen, setWhereToGoOpen] = useState(false);
  const [savedOpen, setSavedOpen] = useState(false);
  const [vaultOpen, setVaultOpen] = useState(false);

  // User Profile (Personalization) & Saved Answer IDs
  const [userProfile, setUserProfile] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('campusiq_profile') || 'null');
    } catch {
      return null;
    }
  });
  const [savedAnswerIds, setSavedAnswerIds] = useState(new Set());

  const activeConvIdRef = useRef(activeConvId);
  useEffect(() => {
    activeConvIdRef.current = activeConvId;
  }, [activeConvId]);

  // Sync theme attribute on document root
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('campusiq_theme', theme);
  }, [theme]);

  // Verify and sync authentication on mount
  useEffect(() => {
    async function syncAuth() {
      try {
        const user = await getMe();
        if (user) {
          setCurrentUser(user);
          if (user.profile && Object.keys(user.profile).length > 0) {
            setUserProfile(user.profile);
          }
        }
      } catch (e) {
        console.warn('Auth sync notice:', e);
      }
    }
    syncAuth();
  }, []);

  // Load conversations on mount or search
  useEffect(() => {
    loadConversationList(searchQuery);
  }, [searchQuery]);

  // Load saved answers when user logs in or changes
  useEffect(() => {
    loadSavedAnswers();
  }, [currentUser]);

  const loadConversationList = async (query = '') => {
    try {
      const data = await getConversations(query);
      setConversations(data);
    } catch (e) {
      console.warn('Failed to load conversations:', e);
    }
  };

  const loadSavedAnswers = async () => {
    if (!currentUser) {
      setSavedAnswerIds(new Set());
      return;
    }
    try {
      const data = await getSavedAnswers();
      const ids = new Set((data || []).map(item => item.message_id || item.id));
      setSavedAnswerIds(ids);
    } catch (e) {
      console.warn('Failed to load saved answer IDs:', e);
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

    setActiveConv((prev) => {
      if (!prev) {
        return {
          id: activeConvIdRef.current || null,
          title: trimmedText.slice(0, 30),
          messages: [tempUserMsg]
        };
      }
      return {
        ...prev,
        messages: [...(prev.messages || []), tempUserMsg]
      };
    });

    setInputMessage('');
    setIsLoading(true);

    try {
      const payload = {
        message: trimmedText,
        conversation_id: activeConvIdRef.current || null
      };

      const response = await sendMessage(payload);

      const assistantMsg = {
        id: response.message_id,
        role: 'assistant',
        content: response.answer,
        sources: response.sources || [],
        created_at: new Date().toISOString()
      };

      setActiveConv((prev) => ({
        id: response.conversation_id,
        title: prev?.title || trimmedText.slice(0, 30),
        messages: [...(prev?.messages || []).filter(m => m.id !== tempUserMsg.id), tempUserMsg, assistantMsg]
      }));

      setActiveConvId(response.conversation_id);
      activeConvIdRef.current = response.conversation_id;

      await loadConversationList(searchQuery);
    } catch (err) {
      console.error('Error sending message:', err);
      const errorMsg = {
        id: `err_${Date.now()}`,
        role: 'assistant',
        content: `Error: ${err.message || 'Failed to retrieve grounded college answer.'}`,
        sources: [],
        created_at: new Date().toISOString()
      };
      setActiveConv((prev) => ({
        id: prev?.id || null,
        title: prev?.title || 'Error',
        messages: [...(prev?.messages || []), errorMsg]
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveAnswer = async (message, question) => {
    if (!currentUser) {
      setGuestPromptFeature('Saving Important Answers');
      setGuestPromptOpen(true);
      return;
    }
    try {
      await saveAnswerApi({
        conversation_id: activeConvIdRef.current || activeConvId || null,
        message_id: message.id,
        question: question || 'Campus Inquiry',
        answer: message.content,
        sources: message.sources || []
      });
      setSavedAnswerIds(prev => new Set([...prev, message.id]));
    } catch (e) {
      if (e.message === 'SIGN_IN_REQUIRED') {
        setGuestPromptFeature('Saving Important Answers');
        setGuestPromptOpen(true);
      } else {
        console.warn('Save answer error:', e);
      }
    }
  };

  const handleUnsaveAnswer = async (messageId) => {
    if (!currentUser) {
      setGuestPromptFeature('Saving Important Answers');
      setGuestPromptOpen(true);
      return;
    }
    try {
      await unsaveByMessageIdApi(messageId);
      setSavedAnswerIds(prev => {
        const next = new Set(prev);
        next.delete(messageId);
        return next;
      });
    } catch (e) {
      console.warn('Unsave error:', e);
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
    if (transcriptText && transcriptText.trim()) {
      setInputMessage(transcriptText.trim());
      setTimeout(() => {
        const textarea = document.querySelector('textarea');
        if (textarea) textarea.focus();
      }, 50);
    }
  };

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  // Auth Handlers
  const handleOpenAuth = (mode = 'login') => {
    setAuthModalInitialMode(mode);
    setAuthModalOpen(true);
  };

  const handleAuthSuccess = (user) => {
    setCurrentUser(user);
    if (user.profile && Object.keys(user.profile).length > 0) {
      setUserProfile(user.profile);
    }
    loadSavedAnswers();
  };

  const handleLogout = () => {
    logoutUser();
    setCurrentUser(null);
    setSavedAnswerIds(new Set());
  };

  const handlePromptGuest = (featureName) => {
    setGuestPromptFeature(featureName);
    setGuestPromptOpen(true);
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
        onOpenMyCampus={() => setMyCampusOpen(true)}
        onOpenPulse={() => setPulseOpen(true)}
        onOpenOpportunities={() => setOpportunitiesOpen(true)}
        onOpenWhereToGo={() => setWhereToGoOpen(true)}
        onOpenSaved={() => setSavedOpen(true)}
        onOpenVault={() => setVaultOpen(true)}
        savedCount={savedAnswerIds.size}
        currentUser={currentUser}
        onOpenAuth={() => handleOpenAuth('login')}
        onLogout={handleLogout}
        onPromptGuest={handlePromptGuest}
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
          currentUser={currentUser}
          onOpenAuth={() => handleOpenAuth('login')}
          onLogout={handleLogout}
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
          savedAnswerIds={savedAnswerIds}
          onSaveAnswer={handleSaveAnswer}
          onUnsaveAnswer={handleUnsaveAnswer}
          userProfile={userProfile}
          onOpenMyCampus={() => {
            if (currentUser) {
              setMyCampusOpen(true);
            } else {
              handlePromptGuest('My Campus Personalization');
            }
          }}
          currentUser={currentUser}
          onOpenAuth={() => handleOpenAuth('login')}
        />
      </main>

      {/* Voice Recording Modal */}
      <VoiceRecorderModal
        isOpen={voiceModalOpen}
        onClose={() => setVoiceModalOpen(false)}
        onApplyTranscript={handleApplyVoiceTranscript}
      />

      {/* 1. My Campus Personalization Modal */}
      <MyCampusModal
        isOpen={myCampusOpen}
        onClose={() => setMyCampusOpen(false)}
        onProfileSaved={(profile) => {
          setUserProfile(profile);
          if (currentUser) {
            updateUserProfile(profile).catch(console.warn);
          }
        }}
      />

      {/* 2. Campus Pulse Modal (Public) */}
      <CampusPulseModal
        isOpen={pulseOpen}
        onClose={() => setPulseOpen(false)}
        onAskAboutUpdate={(query) => handleSendMessage(query)}
      />

      {/* 3. Opportunities Modal (Public) */}
      <OpportunitiesModal
        isOpen={opportunitiesOpen}
        onClose={() => setOpportunitiesOpen(false)}
        onAskAboutOpportunity={(query) => handleSendMessage(query)}
      />

      {/* 4. Where Should I Go Modal (Public) */}
      <WhereToGoModal
        isOpen={whereToGoOpen}
        onClose={() => setWhereToGoOpen(false)}
        onAskAboutLocation={(query) => handleSendMessage(query)}
      />

      {/* 5. Saved Answers Modal (Protected) */}
      <SavedAnswersModal
        isOpen={savedOpen}
        onClose={() => {
          setSavedOpen(false);
          loadSavedAnswers();
        }}
      />

      {/* 6. Personal Knowledge Vault Modal (Protected & Isolated) */}
      <PersonalVaultModal
        isOpen={vaultOpen}
        onClose={() => setVaultOpen(false)}
      />

      {/* Authentication Modal */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onAuthSuccess={handleAuthSuccess}
        onContinueGuest={() => setAuthModalOpen(false)}
        initialMode={authModalInitialMode}
      />

      {/* Guest Sign-In Prompt Modal */}
      <GuestPromptModal
        isOpen={guestPromptOpen}
        onClose={() => setGuestPromptOpen(false)}
        featureName={guestPromptFeature}
        onOpenAuth={() => handleOpenAuth('login')}
      />
    </div>
  );
}
