import React from 'react';
import { X, Lock, ArrowRight, Sparkles, ShieldCheck } from 'lucide-react';

export default function GuestPromptModal({
  isOpen,
  onClose,
  featureName = 'this personalized feature',
  onOpenAuth
}) {
  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.65)',
      backdropFilter: 'blur(5px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: '16px'
    }}>
      <div style={{
        backgroundColor: 'var(--bg-card)',
        borderRadius: '16px',
        width: '100%',
        maxWidth: '420px',
        boxShadow: 'var(--shadow-xl)',
        border: '1px solid var(--border-subtle)',
        overflow: 'hidden',
        textAlign: 'center',
        padding: '28px 24px 22px 24px',
        position: 'relative',
        animation: 'fadeIn 0.2s ease-out'
      }}>
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '14px',
            right: '14px',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: 'var(--text-muted)',
            padding: '6px',
            borderRadius: '50%'
          }}
          aria-label="Close"
        >
          <X size={18} />
        </button>

        <div style={{
          width: '52px',
          height: '52px',
          borderRadius: '50%',
          backgroundColor: 'rgba(122, 28, 40, 0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 16px auto',
          color: 'var(--accent-burgundy)'
        }}>
          <Lock size={24} />
        </div>

        <h3 style={{
          fontSize: '1.18rem',
          fontWeight: 700,
          color: 'var(--text-primary)',
          marginBottom: '8px'
        }}>
          Sign in to use this feature
        </h3>

        <p style={{
          fontSize: '0.86rem',
          color: 'var(--text-secondary)',
          lineHeight: '1.5',
          margin: '0 0 20px 0'
        }}>
          Accessing <strong>{featureName}</strong> requires an authenticated account to keep your saved notes, timetable, and study records private and securely isolated.
        </p>

        <div style={{
          backgroundColor: 'var(--bg-secondary)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '10px',
          padding: '10px 14px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          textAlign: 'left',
          marginBottom: '20px'
        }}>
          <ShieldCheck size={20} color="var(--accent-burgundy)" style={{ flexShrink: 0 }} />
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
            Your personal knowledge vault and bookmarks will remain strictly separated from official college data.
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <button
            onClick={() => {
              onClose();
              if (onOpenAuth) onOpenAuth();
            }}
            style={{
              width: '100%',
              padding: '11px 16px',
              backgroundColor: 'var(--accent-burgundy)',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '8px',
              fontSize: '0.88rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              boxShadow: 'var(--shadow-md)',
              transition: 'background-color 0.15s ease'
            }}
          >
            <span>Sign In / Create Account</span>
            <ArrowRight size={16} />
          </button>

          <button
            onClick={onClose}
            style={{
              width: '100%',
              padding: '10px 16px',
              backgroundColor: 'transparent',
              color: 'var(--text-primary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '8px',
              fontSize: '0.84rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'background-color 0.15s ease'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--bg-secondary)'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            Continue as Guest
          </button>
        </div>
      </div>
    </div>
  );
}
