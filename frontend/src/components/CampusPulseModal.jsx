import React, { useState, useEffect } from 'react';
import { X, Bell, Calendar, MapPin, ExternalLink, MessageSquare, Search, Filter } from 'lucide-react';
import { LinkedinIcon, InstagramIcon, YoutubeIcon } from './BrandIcons';
import { getCampusPulse } from '../services/api';

const CATEGORY_TABS = [
  { id: 'all', label: 'All Updates' },
  { id: 'workshop', label: 'Workshops' },
  { id: 'hackathon', label: 'Hackathons' },
  { id: 'placement', label: 'Placements' },
  { id: 'video', label: 'Videos & Tours' },
  { id: 'cultural', label: 'Campus Culture' }
];

export default function CampusPulseModal({ isOpen, onClose, onAskAboutUpdate }) {
  const [pulseList, setPulseList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedCat, setSelectedCat] = useState('all');
  const [search, setSearch] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadPulse();
    }
  }, [isOpen, selectedCat]);

  const loadPulse = async () => {
    setLoading(true);
    try {
      const data = await getCampusPulse(selectedCat === 'all' ? null : selectedCat);
      setPulseList(data || []);
    } catch (e) {
      console.warn('Failed to load campus pulse:', e);
      setPulseList([]);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const getPlatformIcon = (platform) => {
    const p = (platform || '').toLowerCase();
    if (p.includes('linkedin')) return <LinkedinIcon size={14} color="#0A66C2" />;
    if (p.includes('instagram')) return <InstagramIcon size={14} color="#E4405F" />;
    if (p.includes('youtube')) return <YoutubeIcon size={14} color="#FF0000" />;
    return <Bell size={14} color="var(--accent-burgundy)" />;
  };

  const filtered = pulseList.filter(item => {
    if (!search.trim()) return true;
    const s = search.toLowerCase();
    return item.title.toLowerCase().includes(s) || item.caption.toLowerCase().includes(s);
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
          maxWidth: '740px',
          maxHeight: '90vh',
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
          padding: '20px 24px 14px 24px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              backgroundColor: 'var(--accent-burgundy-light)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-burgundy)'
            }}>
              <Bell size={22} />
            </div>
            <div>
              <h3 style={{
                fontFamily: 'var(--font-display)',
                fontSize: '1.24rem',
                fontWeight: 700,
                color: 'var(--accent-burgundy)',
                margin: 0
              }}>
                Campus Pulse
              </h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0 }}>
                Verified institutional announcements, workshops, hackathons, and achievements.
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

        {/* Category Pills & Search */}
        <div style={{ padding: '12px 24px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '2px' }}>
            {CATEGORY_TABS.map(tab => (
              <button
                key={tab.id}
                onClick={() => setSelectedCat(tab.id)}
                style={{
                  padding: '5px 12px',
                  borderRadius: 'var(--radius-full)',
                  border: selectedCat === tab.id ? '1px solid var(--accent-burgundy)' : '1px solid var(--border-subtle)',
                  backgroundColor: selectedCat === tab.id ? 'var(--accent-burgundy)' : 'var(--bg-card)',
                  color: selectedCat === tab.id ? '#FFFFFF' : 'var(--text-secondary)',
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  transition: 'all 0.15s ease'
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
            <Search size={14} style={{ position: 'absolute', left: '10px', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search verified campus updates..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                width: '100%',
                padding: '7px 10px 7px 32px',
                fontSize: '0.82rem',
                borderRadius: '6px',
                border: '1px solid var(--border-subtle)',
                backgroundColor: 'var(--bg-card-subtle)',
                color: 'var(--text-primary)',
                outline: 'none'
              }}
            />
          </div>
        </div>

        {/* Feed List */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '14px 24px 20px 24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '14px'
        }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
              Loading verified campus updates...
            </div>
          ) : filtered.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '50px 20px',
              color: 'var(--text-muted)',
              fontSize: '0.92rem'
            }}>
              <Bell size={32} style={{ opacity: 0.3, marginBottom: '10px' }} />
              <div>No verified recent campus updates are available.</div>
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
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '7px' }}>
                    {getPlatformIcon(item.source_platform)}
                    <span style={{
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      textTransform: 'uppercase',
                      letterSpacing: '0.06em',
                      color: 'var(--accent-burgundy)'
                    }}>
                      {item.source_platform}
                    </span>
                    {(item.event_date || item.publication_date) && (
                      <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        • {item.event_date ? `Event: ${item.event_date}` : `Published: ${item.publication_date}`}
                      </span>
                    )}
                  </div>

                  <span style={{
                    fontSize: '0.70rem',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    backgroundColor: 'var(--bg-card-subtle)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-muted)',
                    textTransform: 'capitalize'
                  }}>
                    {item.content_type.replace('_', ' ')}
                  </span>
                </div>

                <div style={{ fontSize: '0.94rem', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.3 }}>
                  {item.title}
                </div>

                <div style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {item.caption}
                </div>

                {item.venue && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    <MapPin size={12} color="var(--accent-rose)" />
                    <span>Venue: {item.venue}</span>
                  </div>
                )}

                {/* Card Action Buttons */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginTop: '6px',
                  paddingTop: '8px',
                  borderTop: '1px solid var(--border-subtle)'
                }}>
                  <button
                    onClick={() => {
                      onAskAboutUpdate(`Tell me more about ${item.title}`);
                      onClose();
                    }}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '5px',
                      background: 'none',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: '4px',
                      padding: '4px 10px',
                      fontSize: '0.76rem',
                      fontWeight: 600,
                      color: 'var(--accent-burgundy)',
                      cursor: 'pointer'
                    }}
                  >
                    <MessageSquare size={12} />
                    <span>Ask CampusIQ About This</span>
                  </button>

                  {item.original_url && (
                    <a
                      href={item.original_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        fontSize: '0.76rem',
                        color: 'var(--text-muted)',
                        textDecoration: 'none'
                      }}
                    >
                      <span>Official Link</span>
                      <ExternalLink size={12} />
                    </a>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
