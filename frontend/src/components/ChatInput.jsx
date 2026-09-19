import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp, Mic, Filter, X } from 'lucide-react';

export default function ChatInput({
  inputMessage = '',
  setInputMessage,
  onSendMessage,
  onOpenVoiceRecorder,
  isLoading,
  selectedCategory,
  onClearCategory
}) {
  const textareaRef = useRef(null);

  // Auto-resize textarea when inputMessage changes (including voice updates)
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
    }
  }, [inputMessage]);

  const handleSubmit = (e) => {
    if (e && e.preventDefault) {
      e.preventDefault();
    }
    const trimmed = (inputMessage || '').trim();
    if (!trimmed || isLoading) {
      return;
    }
    onSendMessage(trimmed);
    setInputMessage('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      if (e.shiftKey) {
        // Shift + Enter: create a newline without submitting
        return;
      }
      // Enter without Shift: submit
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleInput = (e) => {
    setInputMessage(e.target.value);
  };

  return (
    <div style={{
      width: '100%',
      maxWidth: '820px',
      margin: '0 auto',
      padding: '0 18px 18px 18px'
    }}>
      {/* Active Category Filter Indicator */}
      {selectedCategory && (
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 10px',
          borderRadius: 'var(--radius-full)',
          backgroundColor: 'var(--accent-burgundy-light)',
          color: 'var(--accent-burgundy)',
          fontSize: '0.78rem',
          fontWeight: 600,
          marginBottom: '8px'
        }}>
          <Filter size={12} />
          <span>Focused on: {selectedCategory}</span>
          <button
            onClick={onClearCategory}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              color: 'var(--accent-burgundy)',
              padding: '1px'
            }}
          >
            <X size={12} />
          </button>
        </div>
      )}

      {/* Main Composer Box */}
      <div
        style={{
          position: 'relative',
          backgroundColor: 'var(--bg-card)',
          border: '1.5px solid var(--border-subtle)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-md)',
          transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
          display: 'flex',
          flexDirection: 'column',
          padding: '10px 14px'
        }}
        onFocus={(e) => {
          e.currentTarget.style.borderColor = 'var(--accent-burgundy)';
          e.currentTarget.style.boxShadow = 'var(--shadow-lg)';
        }}
        onBlur={(e) => {
          e.currentTarget.style.borderColor = 'var(--border-subtle)';
          e.currentTarget.style.boxShadow = 'var(--shadow-md)';
        }}
      >
        <textarea
          ref={textareaRef}
          value={inputMessage}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything about your college..."
          rows={1}
          disabled={isLoading}
          style={{
            width: '100%',
            background: 'transparent',
            border: 'none',
            outline: 'none',
            resize: 'none',
            fontFamily: 'inherit',
            fontSize: '0.96rem',
            lineHeight: 1.5,
            color: 'var(--text-primary)',
            minHeight: '26px',
            maxHeight: '140px',
            paddingRight: '80px'
          }}
        />

        {/* Input Bar Bottom Actions */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginTop: '6px',
          paddingTop: '6px',
          borderTop: '1px solid var(--border-subtle)'
        }}>
          <div />

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {/* Microphone Voice Button */}
            <button
              type="button"
              onClick={onOpenVoiceRecorder}
              disabled={isLoading}
              style={{
                width: '34px',
                height: '34px',
                borderRadius: '50%',
                border: '1px solid var(--border-subtle)',
                backgroundColor: 'var(--bg-card-subtle)',
                color: 'var(--accent-burgundy)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                transition: 'all 0.18s ease'
              }}
              title="Speak college question"
            >
              <Mic size={16} />
            </button>

            {/* Send Button */}
            <button
              type="button"
              onClick={handleSubmit}
              disabled={!inputMessage.trim() || isLoading}
              style={{
                width: '34px',
                height: '34px',
                borderRadius: '50%',
                border: 'none',
                backgroundColor: inputMessage.trim() && !isLoading ? 'var(--accent-burgundy)' : 'var(--border-subtle)',
                color: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: inputMessage.trim() && !isLoading ? 'pointer' : 'default',
                transition: 'all 0.2s ease'
              }}
              title="Send question"
            >
              <ArrowUp size={18} />
            </button>
          </div>
        </div>
      </div>

      <div style={{
        textAlign: 'center',
        marginTop: '8px',
        fontSize: '0.72rem',
        color: 'var(--text-muted)'
      }}>
        CampusIQ provides answers based on verified Prathyusha Engineering College records.
      </div>
    </div>
  );
}
