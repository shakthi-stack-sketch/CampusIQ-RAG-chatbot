import React, { useState } from 'react';
import { 
  Plus, Search, MessageSquare, Trash2, Edit2, Check, X, 
  Sun, Moon, ExternalLink,
  GraduationCap, Bell, Award, MapPin, Bookmark, FolderLock,
  LogIn, LogOut, User
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
  onToggleTheme,
  onOpenMyCampus,
  onOpenPulse,
  onOpenOpportunities,
  onOpenWhereToGo,
  onOpenSaved,
  onOpenVault,
  savedCount = 0,
  currentUser = null,
  onOpenAuth,
  onLogout,
  onPromptGuest
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

          {/* Quick Features Navigation */}
          <div style={{ marginTop: '14px', display: 'flex', flexDirection: 'column', gap: '3px' }}>
            <button
              onClick={() => {
                if (currentUser) {
                  onOpenMyCampus();
                } else if (onPromptGuest) {
                  onPromptGuest('My Campus Personalization');
                } else {
                  onOpenAuth();
                }
              }}
              style={sidebarNavBtnStyle}
              title="Customize student/visitor background"
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--bg-secondary)'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
            >
              <GraduationCap size={15} color="var(--accent-burgundy)" />
              <span>My Campus</span>
            </button>

            <button
              onClick={onOpenPulse}
              style={sidebarNavBtnStyle}
              title="Verified recent college updates"
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--bg-secondary)'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
            >
              <Bell size={15} color="var(--accent-rose)" />
              <span>Campus Pulse</span>
            </button>

            <button
              onClick={onOpenOpportunities}
              style={sidebarNavBtnStyle}
              title="Verified hackathons, workshops & internships"
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--bg-secondary)'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
            >
              <Award size={15} color="#B8860B" />
              <span>Opportunities</span>
            </button>

            <button
              onClick={onOpenWhereToGo}
              style={sidebarNavBtnStyle}
              title="Verified campus office and location guide"
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--bg-secondary)'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
            >
              <MapPin size={15} color="var(--accent-burgundy)" />
              <span>Where Should I Go?</span>
            </button>

            <button
              onClick={() => {
                if (currentUser) {
                  onOpenSaved();
                } else if (onPromptGuest) {
                  onPromptGuest('Saved Answers');
                } else {
                  onOpenAuth();
                }
              }}
              style={sidebarNavBtnStyle}
              title="Saved answers"
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--bg-secondary)'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
            >
              <Bookmark size={15} color="var(--accent-burgundy)" />
              <span style={{ flex: 1, textAlign: 'left' }}>Saved Answers</span>
              {savedCount > 0 && (
                <span style={{
                  fontSize: '0.70rem',
                  padding: '1px 6px',
                  borderRadius: '10px',
                  backgroundColor: 'var(--accent-burgundy-light)',
                  color: 'var(--accent-burgundy)',
                  fontWeight: 700
                }}>
                  {savedCount}
                </span>
              )}
            </button>

            <button
              onClick={() => {
                if (currentUser) {
                  onOpenVault();
                } else if (onPromptGuest) {
                  onPromptGuest('Personal Knowledge Vault');
                } else {
                  onOpenAuth();
                }
              }}
              style={sidebarNavBtnStyle}
              title="Personal study documents"
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--bg-secondary)'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
            >
              <FolderLock size={15} color="var(--text-secondary)" />
              <span>Personal Vault</span>
            </button>
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
          padding: '12px 14px',
          borderTop: '1px solid var(--border-subtle)',
          backgroundColor: 'var(--sidebar-bg)'
        }}>
          {/* User Account / Guest Status */}
          {currentUser ? (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '8px 10px',
              backgroundColor: 'var(--bg-secondary)',
              borderRadius: '8px',
              marginBottom: '10px',
              border: '1px solid var(--border-subtle)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0 }}>
                <div style={{
                  width: '26px',
                  height: '26px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--accent-burgundy)',
                  color: '#FFFFFF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.78rem',
                  fontWeight: 700,
                  flexShrink: 0
                }}>
                  {currentUser.name ? currentUser.name[0].toUpperCase() : 'U'}
                </div>
                <div style={{ minWidth: 0, overflow: 'hidden' }}>
                  <div style={{
                    fontSize: '0.80rem',
                    fontWeight: 600,
                    color: 'var(--text-primary)',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }}>
                    {currentUser.name}
                  </div>
                  <div style={{
                    fontSize: '0.68rem',
                    color: 'var(--text-muted)',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }}>
                    {currentUser.email}
                  </div>
                </div>
              </div>
              <button
                onClick={onLogout}
                title="Sign Out"
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  padding: '4px',
                  borderRadius: '4px',
                  display: 'flex',
                  alignItems: 'center',
                  flexShrink: 0
                }}
                onMouseEnter={(e) => e.currentTarget.style.color = '#DC2626'}
                onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-muted)'}
              >
                <LogOut size={15} />
              </button>
            </div>
          ) : (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '7px 10px',
              backgroundColor: 'var(--bg-secondary)',
              borderRadius: '8px',
              marginBottom: '10px',
              border: '1px solid var(--border-subtle)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{
                  width: '7px',
                  height: '7px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--accent-gold)'
                }} />
                <span style={{ fontSize: '0.76rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                  Guest Mode
                </span>
              </div>
              <button
                onClick={onOpenAuth}
                style={{
                  padding: '4px 10px',
                  backgroundColor: 'var(--accent-burgundy)',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '0.74rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  transition: 'background-color 0.15s ease'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--accent-burgundy-hover)'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--accent-burgundy)'}
              >
                <LogIn size={11} />
                <span>Sign In</span>
              </button>
            </div>
          )}

          {/* Theme Toggle & Official Links */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '2px' }}>
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

const sidebarNavBtnStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '10px',
  padding: '8px 10px',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid transparent',
  backgroundColor: 'transparent',
  color: 'var(--text-primary)',
  fontSize: '0.84rem',
  fontWeight: 600,
  cursor: 'pointer',
  transition: 'background-color 0.15s ease',
  width: '100%',
  textAlign: 'left'
};
