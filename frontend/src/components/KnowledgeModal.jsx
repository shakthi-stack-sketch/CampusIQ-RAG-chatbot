import React, { useState } from 'react';
import { 
  X, ShieldCheck, CheckCircle2, RefreshCw, 
  ExternalLink, GraduationCap, Clock, BookOpen, Building2, Globe
} from 'lucide-react';
import { LinkedinIcon, InstagramIcon, YoutubeIcon } from './BrandIcons';
import { syncKnowledge } from '../services/api';

export default function KnowledgeModal({ isOpen, onClose }) {
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncStatus, setSyncStatus] = useState(null);

  const handleRefresh = async () => {
    setIsSyncing(true);
    setSyncStatus(null);
    try {
      await syncKnowledge();
      setSyncStatus({ success: true, message: 'Campus knowledge base is fully up to date.' });
    } catch (e) {
      setSyncStatus({ success: false, message: 'Could not connect to update service. Please try again.' });
    } finally {
      setIsSyncing(false);
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
          maxWidth: '600px',
          maxHeight: '90vh',
          overflowY: 'auto',
          backgroundColor: 'var(--bg-card)',
          borderRadius: 'var(--radius-lg)',
          border: '1.5px solid var(--border-subtle)',
          boxShadow: 'var(--shadow-lg)',
          padding: '28px 24px',
          position: 'relative'
        }}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '18px',
            right: '18px',
            background: 'none',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            padding: '4px'
          }}
          aria-label="Close dialog"
        >
          <X size={18} />
        </button>

        {/* Modal Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '20px' }}>
          <div style={{
            width: '46px',
            height: '46px',
            borderRadius: '12px',
            backgroundColor: 'var(--accent-burgundy-light)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-burgundy)',
            flexShrink: 0
          }}>
            <ShieldCheck size={26} />
          </div>
          <div>
            <h3 style={{
              fontFamily: 'var(--font-serif)',
              fontSize: '1.35rem',
              color: 'var(--accent-burgundy)',
              fontWeight: 700,
              lineHeight: 1.2
            }}>
              About CampusIQ
            </h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              Prathyusha Engineering College — College Knowledge Assistant
            </p>
          </div>
        </div>

        {/* Informational Pillars Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '10px',
          marginBottom: '20px'
        }}>
          <div style={featureCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <GraduationCap size={16} color="var(--accent-burgundy)" />
              <div style={featureTitleStyle}>Academics & Exams</div>
            </div>
            <div style={featureDescStyle}>
              Internal assessments (IATs), curriculum schedules, and academic calendar dates.
            </div>
          </div>

          <div style={featureCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <Building2 size={16} color="var(--accent-burgundy)" />
              <div style={featureTitleStyle}>Campus & Hostels</div>
            </div>
            <div style={featureDescStyle}>
              Formal dress code norms, weekly mess menus, and hostel gate pass protocols.
            </div>
          </div>

          <div style={featureCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <Clock size={16} color="var(--accent-burgundy)" />
              <div style={featureTitleStyle}>Transport & Timings</div>
            </div>
            <div style={featureDescStyle}>
              College bus routes, morning and evening schedule, and campus office hours.
            </div>
          </div>

          <div style={featureCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <BookOpen size={16} color="var(--accent-burgundy)" />
              <div style={featureTitleStyle}>Verified Sources</div>
            </div>
            <div style={featureDescStyle}>
              Every answer is verified against official handbook records and institutional channels.
            </div>
          </div>
        </div>

        {/* Verified College Channels */}
        <div style={{ marginBottom: '20px' }}>
          <div style={{
            fontSize: '0.78rem',
            fontWeight: 700,
            letterSpacing: '0.06em',
            textTransform: 'uppercase',
            color: 'var(--text-muted)',
            marginBottom: '10px'
          }}>
            Official College Channels & Portals
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <a
              href="https://prathyusha.edu.in"
              target="_blank"
              rel="noreferrer"
              style={sourceRowStyle}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Globe size={16} color="var(--accent-burgundy)" />
                <span style={{ fontWeight: 600, fontSize: '0.86rem' }}>Official College Website</span>
              </div>
              <ExternalLink size={13} color="var(--text-muted)" />
            </a>

            <a
              href="https://www.linkedin.com/school/prathyushaenggcollege/"
              target="_blank"
              rel="noreferrer"
              style={sourceRowStyle}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <LinkedinIcon size={16} color="#0A66C2" />
                <span style={{ fontWeight: 600, fontSize: '0.86rem' }}>Official LinkedIn</span>
              </div>
              <ExternalLink size={13} color="var(--text-muted)" />
            </a>

            <a
              href="https://www.instagram.com/prathyushainstitute/"
              target="_blank"
              rel="noreferrer"
              style={sourceRowStyle}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <InstagramIcon size={16} color="#E4405F" />
                <span style={{ fontWeight: 600, fontSize: '0.86rem' }}>Official Instagram</span>
              </div>
              <ExternalLink size={13} color="var(--text-muted)" />
            </a>

            <a
              href="https://youtube.com/@prathyushaengineeringcollege"
              target="_blank"
              rel="noreferrer"
              style={sourceRowStyle}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <YoutubeIcon size={16} color="#FF0000" />
                <span style={{ fontWeight: 600, fontSize: '0.86rem' }}>Official YouTube Channel</span>
              </div>
              <ExternalLink size={13} color="var(--text-muted)" />
            </a>
          </div>
        </div>

        {/* Update Notice & Result */}
        {syncStatus && (
          <div style={{
            padding: '10px 14px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: syncStatus.success ? 'rgba(46, 204, 113, 0.15)' : 'rgba(231, 76, 60, 0.15)',
            color: syncStatus.success ? '#27AE60' : '#C0392B',
            fontSize: '0.84rem',
            fontWeight: 600,
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <CheckCircle2 size={16} />
            <span>{syncStatus.message}</span>
          </div>
        )}

        {/* Student Notice */}
        <div style={{
          padding: '10px 14px',
          backgroundColor: 'var(--bg-card-subtle)',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-subtle)',
          fontSize: '0.76rem',
          color: 'var(--text-muted)',
          lineHeight: 1.4,
          marginBottom: '18px'
        }}>
          <strong>Note:</strong> CampusIQ answers are strictly referenced from verified institutional documentation. For official certificates, bonafide requests, and fee payments, please visit the college administration office.
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
          <button
            onClick={handleRefresh}
            disabled={isSyncing}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 14px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              backgroundColor: 'transparent',
              color: 'var(--text-secondary)',
              fontSize: '0.84rem',
              fontWeight: 600,
              cursor: isSyncing ? 'default' : 'pointer'
            }}
          >
            <RefreshCw size={13} className={isSyncing ? 'animate-spin' : ''} />
            <span>{isSyncing ? 'Refreshing...' : 'Check for Updates'}</span>
          </button>

          <button
            onClick={onClose}
            style={{
              padding: '8px 20px',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              backgroundColor: 'var(--accent-burgundy)',
              color: '#FFFFFF',
              fontSize: '0.84rem',
              fontWeight: 600,
              cursor: 'pointer',
              boxShadow: 'var(--shadow-sm)'
            }}
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}

const featureCardStyle = {
  backgroundColor: 'var(--bg-card-subtle)',
  border: '1px solid var(--border-subtle)',
  borderRadius: 'var(--radius-sm)',
  padding: '12px 14px'
};

const featureTitleStyle = {
  fontSize: '0.84rem',
  fontWeight: 700,
  color: 'var(--text-primary)'
};

const featureDescStyle = {
  fontSize: '0.74rem',
  color: 'var(--text-muted)',
  lineHeight: 1.35
};

const sourceRowStyle = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: '10px 14px',
  backgroundColor: 'var(--bg-card-subtle)',
  border: '1px solid var(--border-subtle)',
  borderRadius: 'var(--radius-sm)',
  color: 'var(--text-primary)',
  textDecoration: 'none',
  transition: 'border-color 0.15s ease'
};
