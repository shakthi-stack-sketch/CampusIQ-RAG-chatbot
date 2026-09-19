import React, { useRef, useEffect } from 'react';
import MessageItem from './MessageItem';
import WelcomeHero from './WelcomeHero';
import LoadingIndicator from './LoadingIndicator';
import ChatInput from './ChatInput';

export default function ChatArea({
  messages,
  isLoading,
  inputMessage,
  setInputMessage,
  onSendMessage,
  onOpenVoiceRecorder,
  selectedCategory,
  onSelectCategory,
  onClearCategory
}) {
  const scrollContainerRef = useRef(null);
  const isNearBottomRef = useRef(true);
  const prevMessagesCountRef = useRef(messages.length);

  const hasMessages = messages && messages.length > 0;

  // Track if user is near bottom to preserve scroll position when reading older messages
  const handleScroll = () => {
    const el = scrollContainerRef.current;
    if (!el) return;
    const threshold = 120; // px from bottom
    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
    isNearBottomRef.current = distanceFromBottom <= threshold;
  };

  const scrollToBottom = (smooth = true) => {
    const el = scrollContainerRef.current;
    if (!el) return;
    el.scrollTo({
      top: el.scrollHeight,
      behavior: smooth ? 'smooth' : 'auto'
    });
  };

  useEffect(() => {
    const isNewMessage = messages.length > prevMessagesCountRef.current;
    prevMessagesCountRef.current = messages.length;

    const latestMsg = messages[messages.length - 1];
    const isUserMessage = latestMsg && latestMsg.role === 'user';

    // Scroll down if user submitted a message or if already near bottom
    if ((isNewMessage && isUserMessage) || isNearBottomRef.current) {
      requestAnimationFrame(() => {
        scrollToBottom(true);
        isNearBottomRef.current = true;
      });
    }
    // If the user has scrolled up to inspect previous answers, keep their scroll position
  }, [messages, isLoading]);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      flex: 1,
      height: '100%',
      minHeight: 0,
      minWidth: 0,
      overflow: 'hidden',
      backgroundColor: 'var(--bg-primary)',
      position: 'relative'
    }}>
      {/* Scrollable Messages Area */}
      <div
        ref={scrollContainerRef}
        onScroll={handleScroll}
        style={{
          flex: 1,
          minHeight: 0,
          overflowY: 'auto',
          overflowX: 'hidden',
          WebkitOverflowScrolling: 'touch',
          padding: '20px 24px',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {!hasMessages ? (
          <WelcomeHero
            onSelectPrompt={(prompt) => onSendMessage(prompt)}
            onSelectCategory={(cat) => onSelectCategory(cat)}
          />
        ) : (
          <div style={{
            maxWidth: '840px',
            width: '100%',
            margin: '0 auto',
            display: 'flex',
            flexDirection: 'column'
          }}>
            {messages.map((msg, idx) => (
              <MessageItem key={msg.id || idx} message={msg} />
            ))}

            {isLoading && <LoadingIndicator />}
            <div style={{ height: '8px', flexShrink: 0 }} />
          </div>
        )}
      </div>

      {/* Pinned Bottom Composer */}
      <div style={{ flexShrink: 0 }}>
        <ChatInput
          inputMessage={inputMessage}
          setInputMessage={setInputMessage}
          onSendMessage={onSendMessage}
          onOpenVoiceRecorder={onOpenVoiceRecorder}
          isLoading={isLoading}
          selectedCategory={selectedCategory}
          onClearCategory={onClearCategory}
        />
      </div>
    </div>
  );
}

