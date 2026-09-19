import React, { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';

const STATUS_MESSAGES = [
  "Searching campus knowledge...",
  "Finding relevant information...",
  "Retrieving verified college records...",
  "Preparing your answer..."
];

export default function LoadingIndicator() {
  const [msgIndex, setMsgIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setMsgIndex((prev) => (prev + 1) % STATUS_MESSAGES.length);
    }, 2200);
    return () => clearInterval(timer);
  }, []);

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        padding: '16px 20px',
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)',
        maxWidth: '380px',
        marginBottom: '20px',
        boxShadow: 'var(--shadow-sm)'
      }}
    >
      <div style={{
        width: '32px',
        height: '32px',
        borderRadius: '50%',
        backgroundColor: 'var(--accent-burgundy-light)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'var(--accent-burgundy)'
      }}>
        <Loader2 size={18} className="animate-spin" />
      </div>

      <div>
        <div style={{
          fontSize: '0.88rem',
          fontWeight: 500,
          color: 'var(--text-primary)',
          transition: 'all 0.3s ease'
        }}>
          {STATUS_MESSAGES[msgIndex]}
        </div>
      </div>
    </div>
  );
}
