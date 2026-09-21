import React, { useState, useEffect } from 'react';
import { X, Bookmark, Trash2, Copy, Check, ExternalLink, BookOpen, Search } from 'lucide-react';
import { getSavedAnswers, unsaveAnswerApi } from '../services/api';

export default function SavedAnswersModal({ isOpen, onClose }) {
  const [savedList, setSavedList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [copiedId, setCopiedId] = useState(null);

  useEffect(() => {
    if (isOpen) {
      loadSaved();
    }
  }, [isOpen]);

  const loadSaved = async () => {
    setLoading(true);
    try {
      const data = await getSavedAnswers();
      setSavedList(data || []);
    } catch (e) {
      console.warn('Failed to load saved answers:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleUnsave = async (savedId) => {
    try {
      await unsaveAnswerApi(savedId);
      setSavedList(prev => prev.filter(item => item.id !== savedId));
    } catch (e) {
      console.warn('Failed to unsave:', e);
    }
  };

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  if (!isOpen) return null;

  const filtered = savedList.filter(item => {
    if (!search.trim()) return true;
    const s = search.toLowerCase();
    return item.question.toLowerCase().includes(s) || item.answer.toLowerCase().includes(s);
  });

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.55)',
        backdropFilter: 'blur(4px)',
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px'
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '100%',
          maxWidth: '680px',
          maxHeight: '88vh',
          backgroundColor: 'var(--bg-card)',
          borderRadius: 'var(--radius-lg)',
          border: '1.5px solid var(--border-subtle)',
          boxShadow: 'var(--shadow-lg)',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {/* Header */}
        <div style={{
          padding: '20px 24px 16px 24px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              backgroundColor: 'var(--accent-burgundy-light)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-burgundy)'
            }}>
              <Bookmark size={20} />
            </div>
            <div>
              <h3 style={{
                fontFamily: 'var(--font-display)',
                fontSize: '1.18rem',
                fontWeight: 700,
                color: 'var(--accent-burgundy)',
                margin: 0
              }}>
                Saved Answers
              </h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0 }}>
                Important verified college information bookmarked for quick reference.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '4px'
            }}
            aria-label="Close"
          >
            <X size={18} />
          </button>
        </div>

        {/* Search Bar */}
        <div style={{ padding: '12px 24px 8px 24px' }}>
          <div style={{
            position: 'relative',
            display: 'flex',
            alignItems: 'center'
          }}>
            <Search size={14} style={{ position: 'absolute', left: '10px', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search in saved answers..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                width: '100%',
                padding: '8px 10px 8px 32px',
                fontSize: '0.84rem',
                borderRadius: '6px',
                border: '1px solid var(--border-subtle)',
                backgroundColor: 'var(--bg-card-subtle)',
                color: 'var(--text-primary)',
                outline: 'none'
              }}
            />
          </div>
        </div>

        {/* Content List */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '12px 24px 20px 24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '14px'
        }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
              Loading saved answers...
            </div>
          ) : filtered.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '50px 20px',
              color: 'var(--text-muted)',
              fontSize: '0.92rem'
            }}>
              <Bookmark size={32} style={{ opacity: 0.3, marginBottom: '10px' }} />
              <div>You haven't saved any answers yet.</div>
              <div style={{ fontSize: '0.78rem', marginTop: '4px', opacity: 0.7 }}>
                Click [Save Answer] under any response to pin it here.
              </div>
            </div>
          ) : (
            filtered.map((item) => (
              <div
                key={item.id}
                style={{
                  backgroundColor: 'var(--bg-card)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '16px',
                  boxShadow: 'var(--shadow-sm)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px'
                }}
              >
                {/* Question */}
                <div style={{
                  fontSize: '0.88rem',
                  fontWeight: 700,
                  color: 'var(--accent-burgundy)'
                }}>
                  {item.question}
                </div>

                {/* Answer Preview */}
                <div style={{
                  fontSize: '0.84rem',
                  lineHeight: 1.5,
                  color: 'var(--text-primary)',
                  whiteSpace: 'pre-wrap'
                }}>
                  {item.answer}
                </div>

                {/* Sources & Action Footer */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: '8px',
                  marginTop: '6px',
                  paddingTop: '8px',
                  borderTop: '1px solid var(--border-subtle)',
                  fontSize: '0.75rem',
                  color: 'var(--text-muted)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <BookOpen size={12} />
                    <span>
                      {item.sources && item.sources.length > 0
                        ? `${item.sources.length} verified source(s)`
                        : 'Official College Record'}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <button
                      onClick={() => handleCopy(item.id, item.answer)}
                      style={cardActionBtnStyle}
                      title="Copy text"
                    >
                      {copiedId === item.id ? <Check size={12} color="green" /> : <Copy size={12} />}
                      <span>{copiedId === item.id ? 'Copied' : 'Copy'}</span>
                    </button>

                    <button
                      onClick={() => handleUnsave(item.id)}
                      style={{ ...cardActionBtnStyle, color: '#E74C3C' }}
                      title="Unsave answer"
                    >
                      <Trash2 size={12} />
                      <span>Unsave</span>
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

const cardActionBtnStyle = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: '4px',
  background: 'none',
  border: '1px solid var(--border-subtle)',
  borderRadius: '4px',
  padding: '3px 8px',
  fontSize: '0.75rem',
  color: 'var(--text-muted)',
  cursor: 'pointer'
};
