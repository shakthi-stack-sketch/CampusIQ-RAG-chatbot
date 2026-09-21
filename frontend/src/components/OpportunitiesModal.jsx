import React, { useState, useEffect } from 'react';
import { X, Award, Calendar, MapPin, ExternalLink, MessageSquare, CheckCircle, ShieldCheck } from 'lucide-react';
import { getVerifiedOpportunities } from '../services/api';

const OPPORTUNITY_CATEGORIES = [
  { id: 'all', label: 'All Opportunities' },
  { id: 'workshops', label: 'Workshops' },
  { id: 'hackathons', label: 'Hackathons' },
  { id: 'seminars', label: 'Seminars' },
  { id: 'training', label: 'Placements & Training' },
  { id: 'competitions', label: 'Competitions' }
];

export default function OpportunitiesModal({ isOpen, onClose, onAskAboutOpportunity }) {
  const [oppList, setOppList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedCat, setSelectedCat] = useState('all');

  useEffect(() => {
    if (isOpen) {
      loadOpportunities();
    }
  }, [isOpen, selectedCat]);

  const loadOpportunities = async () => {
    setLoading(true);
    try {
      const data = await getVerifiedOpportunities(selectedCat === 'all' ? null : selectedCat);
      setOppList(data || []);
    } catch (e) {
      console.warn('Failed to load opportunities:', e);
      setOppList([]);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

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
              backgroundColor: 'var(--accent-gold-light, rgba(212, 175, 55, 0.15))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-burgundy)'
            }}>
              <Award size={22} />
            </div>
            <div>
              <h3 style={{
                fontFamily: 'var(--font-display)',
                fontSize: '1.24rem',
                fontWeight: 700,
                color: 'var(--accent-burgundy)',
                margin: 0
              }}>
                Opportunity Finder
              </h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0 }}>
                Verified technical workshops, national hackathons, guest lectures, and placement drives.
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

        {/* Category Pills */}
        <div style={{ padding: '12px 24px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', gap: '6px', overflowX: 'auto' }}>
          {OPPORTUNITY_CATEGORIES.map(tab => (
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

        {/* Content List */}
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
              Loading verified opportunities...
            </div>
          ) : oppList.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '50px 20px',
              color: 'var(--text-muted)',
              fontSize: '0.92rem'
            }}>
              <Award size={32} style={{ opacity: 0.3, marginBottom: '10px' }} />
              <div>No verified opportunities are currently available.</div>
            </div>
          ) : (
            oppList.map((item) => (
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
                  <span style={{
                    fontSize: '0.72rem',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    backgroundColor: 'var(--accent-burgundy-light)',
                    color: 'var(--accent-burgundy)',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    {item.category}
                  </span>

                  {item.date && (
                    <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Calendar size={12} />
                      <span>{item.date}</span>
                    </span>
                  )}
                </div>

                <div style={{ fontSize: '0.94rem', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.3 }}>
                  {item.title}
                </div>

                <div style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {item.description}
                </div>

                {/* Eligibility / Registration Details (Only if actually available) */}
                {item.eligibility && (
                  <div style={{
                    fontSize: '0.78rem',
                    padding: '6px 10px',
                    borderRadius: '4px',
                    backgroundColor: 'var(--bg-card-subtle)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-primary)'
                  }}>
                    <strong>Requirements:</strong> {item.eligibility}
                  </div>
                )}

                {item.venue && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    <MapPin size={12} color="var(--accent-rose)" />
                    <span>Venue: {item.venue}</span>
                  </div>
                )}

                {/* Footer Action */}
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
                      onAskAboutOpportunity(`What are the details and eligibility for ${item.title}?`);
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
                    <span>Ask Details</span>
                  </button>

                  {/* Application link ONLY if actually available */}
                  {item.application_link ? (
                    <a
                      href={item.application_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        fontSize: '0.76rem',
                        fontWeight: 600,
                        color: 'var(--accent-burgundy)',
                        textDecoration: 'none'
                      }}
                    >
                      <span>Official Link</span>
                      <ExternalLink size={12} />
                    </a>
                  ) : null}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
