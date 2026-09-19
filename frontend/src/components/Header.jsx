import React from 'react';

export default function Header({
  activeConvTitle,
  hasMessages
}) {
  // If no conversation messages exist yet, keep header hidden to prevent duplicate 'New Conversation' branding
  if (!hasMessages) {
    return null;
  }

  return (
    <header
      style={{
        height: '46px',
        borderBottom: '1px solid var(--border-subtle)',
        backgroundColor: 'var(--bg-primary)',
        display: 'flex',
        alignItems: 'center',
        padding: '0 24px',
        flexShrink: 0,
        zIndex: 10
      }}
    >
      <h2 style={{
        fontSize: '0.92rem',
        fontWeight: 600,
        color: 'var(--text-primary)',
        maxWidth: '650px',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
        margin: 0
      }}>
        {activeConvTitle || 'Conversation'}
      </h2>
    </header>
  );
}


