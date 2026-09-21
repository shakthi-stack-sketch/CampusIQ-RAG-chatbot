import React, { useState, useEffect } from 'react';
import { X, MapPin, Building, Search, MessageSquare, ShieldCheck, HelpCircle } from 'lucide-react';
import { getVerifiedLocations } from '../services/api';

export default function WhereToGoModal({ isOpen, onClose, onAskAboutLocation }) {
  const [locations, setLocations] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadLocations();
    }
  }, [isOpen]);

  const loadLocations = async () => {
    setLoading(true);
    try {
      const data = await getVerifiedLocations();
      setLocations(data || []);
    } catch (e) {
      console.warn('Failed to load locations:', e);
      setLocations([]);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const filtered = locations.filter(loc => {
    if (!search.trim()) return true;
    const s = search.toLowerCase();
    return loc.name.toLowerCase().includes(s) || loc.building.toLowerCase().includes(s) || loc.purpose.toLowerCase().includes(s);
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
          maxWidth: '720px',
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
              <MapPin size={22} />
            </div>
            <div>
              <h3 style={{
                fontFamily: 'var(--font-display)',
                fontSize: '1.24rem',
                fontWeight: 700,
                color: 'var(--accent-burgundy)',
                margin: 0
              }}>
                Where Should I Go?
              </h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0 }}>
                Verified campus offices, academic halls, laboratories, and administrative venues.
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

        {/* Notice */}
        <div style={{
          padding: '10px 24px',
          backgroundColor: 'var(--bg-card-subtle)',
          borderBottom: '1px solid var(--border-subtle)',
          fontSize: '0.76rem',
          color: 'var(--text-muted)'
        }}>
          <strong>Note:</strong> CampusIQ provides location guidance ONLY from verified college documentation. Room numbers or offices not in records will never be guessed.
        </div>

        {/* Search */}
        <div style={{ padding: '12px 24px' }}>
          <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
            <Search size={14} style={{ position: 'absolute', left: '10px', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search office, lab, or building..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                width: '100%',
                padding: '7px 10px 7px 32px',
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

        {/* Location List */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '4px 24px 20px 24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px'
        }}>
          {filtered.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '40px 20px',
              color: 'var(--text-muted)',
              fontSize: '0.88rem'
            }}>
              I couldn't find verified information about that office or location in the available college sources.
            </div>
          ) : (
            filtered.map((loc) => (
              <div
                key={loc.id}
                style={{
                  backgroundColor: 'var(--bg-card)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '14px 16px',
                  boxShadow: 'var(--shadow-sm)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ fontWeight: 700, fontSize: '0.94rem', color: 'var(--text-primary)' }}>
                    {loc.name}
                  </div>
                  <span style={{
                    fontSize: '0.70rem',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    backgroundColor: 'var(--accent-burgundy-light)',
                    color: 'var(--accent-burgundy)',
                    fontWeight: 600
                  }}>
                    {loc.category}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.80rem', color: 'var(--accent-rose)' }}>
                  <Building size={13} />
                  <span>{loc.building}</span>
                </div>

                <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                  {loc.purpose}
                </div>

                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginTop: '4px',
                  paddingTop: '6px',
                  borderTop: '1px solid var(--border-subtle)',
                  fontSize: '0.74rem',
                  color: 'var(--text-muted)'
                }}>
                  <span>Source: {loc.source}</span>

                  <button
                    onClick={() => {
                      onAskAboutLocation(`Where is the ${loc.name} located and what are its procedures?`);
                      onClose();
                    }}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                      background: 'none',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: '4px',
                      padding: '3px 8px',
                      fontSize: '0.74rem',
                      fontWeight: 600,
                      color: 'var(--accent-burgundy)',
                      cursor: 'pointer'
                    }}
                  >
                    <MessageSquare size={11} />
                    <span>Ask CampusIQ</span>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
