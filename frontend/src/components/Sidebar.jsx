import React, { useState } from 'react';
import { 
  Plus, Search, MessageSquare, Trash2, Edit2, Check, X, 
  Sun, Moon, ExternalLink
} from 'lucide-react';

export default function Sidebar({
  conversations,
  activeConvId,
  onSelectConversation,
  onNewChat,
  onRenameConversation,
  onDeleteConversation,
  searchQuery,
  onSearchChange,
  theme,
  onToggleTheme
}) {
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  const startRename = (conv, e) => {
    e.stopPropagation();
    setEditingId(conv.id);
    setEditTitle(conv.title);
  };

  const submitRename = (convId, e) => {
    e.stopPropagation();
    if (editTitle.trim()) {
      onRenameConversation(convId, editTitle.trim());
    }
    setEditingId(null);
  };

  const cancelRename = (e) => {
    e.stopPropagation();
    setEditingId(null);
  };

  const handleDelete = (convId, e) => {
    e.stopPropagation();
    if (window.confirm('Delete this conversation?')) {
      onDeleteConversation(convId);
    }
  };

  const renderGroup = (title, list) => {
    if (!list || list.length === 0) return null;
    return (
      <div style={{ marginBottom: '18px' }}>
        <div style={{
          fontSize: '0.72rem',
          fontWeight: 700,
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
          color: 'var(--text-muted)',
          padding: '0 12px 6px 12px'
        }}>
          {title}
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
          {list.map((c) => {
            const isActive = c.id === activeConvId;
            const isEditing = editingId === c.id;

            return (
              <div
                key={c.id}
                onClick={() => {
                  if (!isEditing) {
                    onSelectConversation(c.id);
                  }
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '9px 12px',
                  borderRadius: 'var(--radius-sm)',
                  cursor: 'pointer',
                  backgroundColor: isActive ? 'var(--accent-burgundy-light)' : 'transparent',
                  border: isActive ? '1px solid var(--accent-burgundy)' : '1px solid transparent',
                  color: isActive ? 'var(--accent-burgundy)' : 'var(--text-primary)',
                  fontWeight: isActive ? 600 : 400,
                  fontSize: '0.88rem',
                  transition: 'all 0.18s ease'
                }}
                onMouseEnter={(e) => {
                  if (!isActive) e.currentTarget.style.backgroundColor = 'var(--bg-secondary)';
                }}
                onMouseLeave={(e) => {
                  if (!isActive) e.currentTarget.style.backgroundColor = 'transparent';
                }}
              >
                {isEditing ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', width: '100%' }} onClick={(e) => e.stopPropagation()}>
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') submitRename(c.id, e);
                        if (e.key === 'Escape') cancelRename(e);
                      }}
                      autoFocus
                      style={{
                        flex: 1,
                        padding: '4px 8px',
                        fontSize: '0.84rem',
                        borderRadius: '4px',
                        border: '1px solid var(--accent-burgundy)',
                        backgroundColor: 'var(--bg-card)',
                        color: 'var(--text-primary)',
                        outline: 'none'
                      }}
                    />
                    <button onClick={(e) => submitRename(c.id, e)} style={actionBtnStyle} title="Save">
                      <Check size={14} color="var(--accent-burgundy)" />
                    </button>
                    <button onClick={cancelRename} style={actionBtnStyle} title="Cancel">
                      <X size={14} color="var(--text-muted)" />
                    </button>
                  </div>
                ) : (
                  <>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '9px', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                      <MessageSquare size={15} style={{ flexShrink: 0, opacity: isActive ? 1 : 0.6 }} />
                      <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.title}</span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <button
                        onClick={(e) => startRename(c, e)}
                        style={actionBtnStyle}
                        title="Rename"
                      >
                        <Edit2 size={13} />
                      </button>
                      <button
                        onClick={(e) => handleDelete(c.id, e)}
                        style={actionBtnStyle}
                        title="Delete"
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <aside
      style={{
        width: '280px',
        backgroundColor: 'var(--sidebar-bg)',
        borderRight: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        zIndex: 50,
        flexShrink: 0,
        height: '100%',
        boxShadow: 'var(--shadow-sm)'
      }}
    >
        {/* Brand Header */}
        <div style={{ padding: '18px 16px 14px 16px', borderBottom: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{
              backgroundColor: '#FFFFFF',
              padding: '6px 14px',
              borderRadius: '8px',
              border: '1px solid var(--accent-gold)',
              boxShadow: 'var(--shadow-sm)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <img
                src="/college_logo.jpeg"
                alt="Prathyusha Engineering College"
                style={{
                  width: '100%',
                  maxHeight: '38px',
                  objectFit: 'contain',
                  display: 'block'
                }}
              />
            </div>
            <div style={{ padding: '0 2px' }}>
              <div style={{
                fontFamily: 'var(--font-display)',
                fontWeight: 700,
                fontSize: '1.1rem',
                color: 'var(--accent-burgundy)',
                letterSpacing: '0.06em'
              }}>
                CAMPUSIQ
              </div>
              <div style={{
                fontSize: '0.76rem',
                color: 'var(--text-primary)',
                fontWeight: 600,
                marginTop: '1px'
              }}>
                Prathyusha Engineering College
              </div>
              <div style={{
                fontSize: '0.68rem',
                color: 'var(--text-muted)',
                fontWeight: 500
              }}>
                College Knowledge Assistant
              </div>
            </div>
          </div>

          {/* New Chat Button */}
          <button
            onClick={onNewChat}
            style={{
              marginTop: '16px',
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              padding: '10px 14px',
              backgroundColor: 'var(--accent-burgundy)',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: 'var(--radius-sm)',
              fontWeight: 600,
              fontSize: '0.88rem',
              cursor: 'pointer',
              boxShadow: 'var(--shadow-md)',
              transition: 'background-color 0.2s ease, transform 0.1s ease'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--accent-burgundy-hover)'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--accent-burgundy)'}
          >
            <Plus size={16} />
            <span>New Conversation</span>
          </button>

          {/* Search Input */}
          <div style={{
            position: 'relative',
            marginTop: '12px',
            display: 'flex',
            alignItems: 'center'
          }}>
            <Search size={14} style={{ position: 'absolute', left: '10px', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              style={{
                width: '100%',
                padding: '7px 10px 7px 32px',
                fontSize: '0.82rem',
                borderRadius: '6px',
                border: '1px solid var(--border-subtle)',
                backgroundColor: 'var(--bg-card)',
                color: 'var(--text-primary)',
                outline: 'none'
              }}
            />
          </div>
        </div>

        {/* Scrollable Conversation History */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '14px 12px' }}>
          {renderGroup('Today', conversations?.today)}
          {renderGroup('Yesterday', conversations?.yesterday)}
          {renderGroup('Earlier', conversations?.earlier)}

          {(!conversations?.today?.length && !conversations?.yesterday?.length && !conversations?.earlier?.length) && (
            <div style={{
              textAlign: 'center',
              padding: '30px 15px',
              color: 'var(--text-muted)',
              fontSize: '0.84rem'
            }}>
              No previous chats found.<br />Start a new conversation!
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div style={{
          padding: '14px 16px',
          borderTop: '1px solid var(--border-subtle)',
          backgroundColor: 'var(--sidebar-bg)'
        }}>
          {/* Theme Toggle & Official Links */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '4px' }}>
            <button
              onClick={onToggleTheme}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                background: 'none',
                border: 'none',
                color: 'var(--text-secondary)',
                fontSize: '0.8rem',
                cursor: 'pointer',
                padding: '6px 8px',
                borderRadius: '6px'
              }}
              title="Toggle theme"
            >
              {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
              <span>{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
            </button>

            <a
              href="https://prathyusha.edu.in"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                color: 'var(--text-muted)',
                fontSize: '0.78rem',
                textDecoration: 'none'
              }}
            >
              <span>PEC Web</span>
              <ExternalLink size={12} />
            </a>
          </div>
        </div>
      </aside>
  );
}

const actionBtnStyle = {
  background: 'none',
  border: 'none',
  padding: '4px',
  cursor: 'pointer',
  borderRadius: '4px',
  color: 'var(--text-muted)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  transition: 'color 0.15s ease'
};
