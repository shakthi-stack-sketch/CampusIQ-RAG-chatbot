import React from 'react';
import { LogIn, LogOut, User } from 'lucide-react';

export default function Header({
  activeConvTitle,
  hasMessages,
  currentUser,
  onOpenAuth,
  onLogout
}) {
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
        justifyContent: 'space-between',
        padding: '0 24px',
        flexShrink: 0,
        zIndex: 10
      }}
    >
      <h2 style={{
        fontSize: '0.92rem',
        fontWeight: 600,
        color: 'var(--text-primary)',
        maxWidth: '550px',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
        margin: 0
      }}>
        {activeConvTitle || 'Conversation'}
      </h2>

      {/* Right Header Status / Auth Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        {currentUser ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              width: '24px',
              height: '24px',
              borderRadius: '50%',
              backgroundColor: 'var(--accent-burgundy)',
              color: '#FFFFFF',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.74rem',
              fontWeight: 700
            }}>
              {currentUser.name ? currentUser.name[0].toUpperCase() : 'U'}
            </div>
            <span style={{ fontSize: '0.80rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              {currentUser.name}
            </span>
            <button
              onClick={onLogout}
              title="Sign Out"
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                padding: '4px',
                display: 'flex',
                alignItems: 'center'
              }}
              onMouseEnter={(e) => e.currentTarget.style.color = '#DC2626'}
              onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-muted)'}
            >
              <LogOut size={14} />
            </button>
          </div>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
              Guest
            </span>
            <button
              onClick={onOpenAuth}
              style={{
                padding: '4px 10px',
                backgroundColor: 'var(--accent-burgundy)',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '6px',
                fontSize: '0.76rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <LogIn size={11} />
              <span>Sign In</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
