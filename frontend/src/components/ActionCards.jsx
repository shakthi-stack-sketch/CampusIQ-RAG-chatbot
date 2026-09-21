import React, { useState } from 'react';
import { Bookmark, BookmarkCheck, ExternalLink, MessageSquare, Compass, FileText } from 'lucide-react';

export default function ActionCards({
  message,
  onSave,
  onUnsave,
  isSaved,
  onAskFollowup,
  onExploreClubs
}) {
  const [saveLoading, setSaveLoading] = useState(false);

  const handleToggleSave = async () => {
    if (saveLoading) return;
    setSaveLoading(true);
    try {
      if (isSaved) {
        await onUnsave(message.id);
      } else {
        await onSave(message);
      }
    } catch (e) {
      console.warn('Save toggle error:', e);
    } finally {
      setSaveLoading(false);
    }
  };

  const contentLower = (message.content || '').toLowerCase();
  const mentionsClubs = contentLower.includes('club') || contentLower.includes('yantramanav') || contentLower.includes('drones');
  const hasValidSourceUrl = message.sources && message.sources.some(s => Boolean(s.url));
  const primarySourceUrl = hasValidSourceUrl ? message.sources.find(s => Boolean(s.url))?.url : null;

  // Generate verified contextual follow-up prompt
  let followupPrompt = null;
  if (contentLower.includes('mess') || contentLower.includes('menu') || contentLower.includes('breakfast') || contentLower.includes('lunch')) {
    if (contentLower.includes('wednesday')) followupPrompt = "What is the mess menu on Thursday?";
    else if (contentLower.includes('monday')) followupPrompt = "What is the mess menu on Tuesday?";
    else followupPrompt = "What is the complete weekly mess menu?";
  } else if (contentLower.includes('dress') || contentLower.includes('uniform')) {
    followupPrompt = "What is the dress code on Thursday to Saturday?";
  } else if (contentLower.includes('hostel')) {
    followupPrompt = "What are the hostel leave procedures and card colors?";
  } else if (mentionsClubs) {
    followupPrompt = "Tell me more about the Google Developer Club and Drones Club.";
  } else if (contentLower.includes('iat') || contentLower.includes('assessment') || contentLower.includes('exam')) {
    followupPrompt = "When is the model examination scheduled?";
  } else if (contentLower.includes('bus') || contentLower.includes('route')) {
    followupPrompt = "What are the bus boarding timings for Thandalam and Avadi?";
  }

  return (
    <div style={{
      display: 'flex',
      flexWrap: 'wrap',
      gap: '8px',
      marginTop: '10px',
      paddingTop: '8px',
      borderTop: '1px solid var(--border-subtle)'
    }}>
      {/* 1. Save / Unsave Answer */}
      <button
        onClick={handleToggleSave}
        disabled={saveLoading}
        style={{
          ...actionCardBtnStyle,
          backgroundColor: isSaved ? 'var(--accent-burgundy-light)' : 'var(--bg-card)',
          color: isSaved ? 'var(--accent-burgundy)' : 'var(--text-secondary)',
          borderColor: isSaved ? 'var(--accent-burgundy)' : 'var(--border-subtle)'
        }}
        title={isSaved ? "Saved to your list" : "Save this verified answer"}
      >
        {isSaved ? <BookmarkCheck size={13} color="var(--accent-burgundy)" /> : <Bookmark size={13} />}
        <span>{isSaved ? 'Saved' : 'Save Answer'}</span>
      </button>

      {/* 2. View Source (Only when a verified working link exists) */}
      {primarySourceUrl && (
        <a
          href={primarySourceUrl}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            ...actionCardBtnStyle,
            textDecoration: 'none'
          }}
          title="Open official verified source"
        >
          <ExternalLink size={13} color="var(--accent-burgundy)" />
          <span>View Source</span>
        </a>
      )}

      {/* 3. Ask Follow-up (Contextually grounded prompt) */}
      {followupPrompt && onAskFollowup && (
        <button
          onClick={() => onAskFollowup(followupPrompt)}
          style={actionCardBtnStyle}
          title={`Ask: "${followupPrompt}"`}
        >
          <MessageSquare size={13} color="var(--accent-rose)" />
          <span>Ask Follow-up</span>
        </button>
      )}

      {/* 4. Explore Clubs (Only when clubs/innovation are mentioned) */}
      {mentionsClubs && onExploreClubs && (
        <button
          onClick={onExploreClubs}
          style={actionCardBtnStyle}
          title="Explore technical clubs and innovation domains"
        >
          <Compass size={13} color="var(--accent-burgundy)" />
          <span>Explore Clubs</span>
        </button>
      )}
    </div>
  );
}

const actionCardBtnStyle = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: '6px',
  padding: '5px 11px',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid var(--border-subtle)',
  backgroundColor: 'var(--bg-card)',
  color: 'var(--text-secondary)',
  fontSize: '0.78rem',
  fontWeight: 600,
  cursor: 'pointer',
  transition: 'all 0.15s ease',
  boxShadow: 'var(--shadow-sm)'
};
