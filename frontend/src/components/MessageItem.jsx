import React, { useState } from 'react';
import { marked } from 'marked';
import { 
  Copy, Check, Volume2, ExternalLink, Globe, BookOpen 
} from 'lucide-react';
import { LinkedinIcon, InstagramIcon, YoutubeIcon } from './BrandIcons';

export default function MessageItem({ message }) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSpeak = () => {
    if (!window.speechSynthesis) return;

    if (isPlaying) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
      return;
    }

    // Clean markdown symbols for speech synthesis
    const cleanSpeech = message.content
      .replace(/[#*`_~]/g, '')
      .replace(/\[.*?\]\(.*?\)/g, '')
      .replace(/<[^>]*>/g, '')
      .trim();

    const utterance = new SpeechSynthesisUtterance(cleanSpeech);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.onend = () => setIsPlaying(false);
    utterance.onerror = () => setIsPlaying(false);

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
    setIsPlaying(true);
  };

  const getSourceIcon = (platform) => {
    const p = (platform || '').toLowerCase();
    if (p.includes('linkedin')) return <LinkedinIcon size={14} color="#0A66C2" />;
    if (p.includes('instagram')) return <InstagramIcon size={14} color="#E4405F" />;
    if (p.includes('youtube')) return <YoutubeIcon size={14} color="#FF0000" />;
    if (p.includes('website')) return <Globe size={14} color="var(--accent-burgundy)" />;
    return <BookOpen size={14} color="var(--accent-burgundy)" />;
  };

  const getSourceButtonLabel = (platform) => {
    const p = (platform || '').toLowerCase();
    if (p.includes('linkedin')) return 'View on LinkedIn';
    if (p.includes('youtube')) return 'Watch on YouTube';
    if (p.includes('instagram')) return 'View on Instagram';
    if (p.includes('website')) return 'View on College Website';
    return 'View Source';
  };

  const htmlContent = marked.parse(message.content || '');

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: isUser ? 'flex-end' : 'flex-start',
        marginBottom: '28px',
        width: '100%'
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: isUser ? '78%' : '88%'
        }}
      >
        {/* Sender Name Label */}
        <div
          style={{
            fontSize: isUser ? '0.78rem' : '0.86rem',
            fontWeight: 700,
            color: isUser ? 'var(--text-muted)' : 'var(--accent-burgundy)',
            letterSpacing: isUser ? '0.02em' : '0.05em',
            marginBottom: '6px',
            textAlign: isUser ? 'right' : 'left'
          }}
        >
          {isUser ? 'User' : 'CampusIQ'}
        </div>

        {/* Message Bubble */}
        <div
          style={{
            padding: isUser ? '12px 18px' : '18px 22px',
            borderRadius: isUser ? '18px 4px 18px 18px' : '4px 18px 18px 18px',
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            boxShadow: 'var(--shadow-sm)',
            color: 'var(--text-primary)'
          }}
        >
          {isUser ? (
            <div style={{ fontSize: '0.96rem', lineHeight: 1.5, whiteSpace: 'pre-wrap' }}>
              {message.content}
            </div>
          ) : (
            <div
              className="markdown-body"
              dangerouslySetInnerHTML={{ __html: htmlContent }}
            />
          )}
        </div>

        {/* Assistant Action Bar & Sources */}
        {!isUser && (
          <div style={{ marginTop: '10px' }}>
            {/* Utility actions: Copy, Read Aloud */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <button
                onClick={handleCopy}
                style={actionBtnStyle}
                title="Copy answer"
              >
                {copied ? <Check size={13} color="green" /> : <Copy size={13} />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>

              <button
                onClick={handleSpeak}
                style={actionBtnStyle}
                title={isPlaying ? 'Stop listening' : 'Listen to answer'}
              >
                <Volume2 size={13} color={isPlaying ? 'var(--accent-burgundy)' : 'currentColor'} />
                <span>{isPlaying ? 'Speaking...' : 'Listen'}</span>
              </button>
            </div>

            {/* Verified Sources Section */}
            {message.sources && message.sources.length > 0 && (
              <div
                style={{
                  backgroundColor: 'var(--bg-card-subtle)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '10px 14px',
                  marginTop: '10px'
                }}
              >
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '0.74rem',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em',
                  color: 'var(--accent-burgundy)',
                  marginBottom: '8px'
                }}>
                  <BookOpen size={13} />
                  <span>Verified Source</span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {message.sources.map((src, i) => (
                    <div
                      key={i}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        flexWrap: 'wrap',
                        gap: '8px',
                        padding: '8px 12px',
                        backgroundColor: 'var(--bg-card)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: '6px'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: '180px' }}>
                        {getSourceIcon(src.platform)}
                        <div>
                          <div style={{ fontWeight: 600, fontSize: '0.84rem', color: 'var(--text-primary)' }}>
                            {src.title}
                          </div>
                          {(src.department || src.publication_date) && (
                            <div style={{ fontSize: '0.70rem', color: 'var(--text-muted)' }}>
                              {[src.department, src.publication_date].filter(Boolean).join(' • ')}
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Display View Source button only if source URL is valid and verified */}
                      {src.url ? (
                        <a
                          href={src.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '5px',
                            padding: '4px 10px',
                            backgroundColor: 'var(--bg-card-subtle)',
                            border: '1px solid var(--border-subtle)',
                            borderRadius: '6px',
                            color: 'var(--accent-burgundy)',
                            fontSize: '0.78rem',
                            fontWeight: 600,
                            textDecoration: 'none',
                            transition: 'all 0.15s ease'
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.backgroundColor = 'var(--accent-burgundy-light)';
                            e.currentTarget.style.borderColor = 'var(--accent-burgundy)';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.backgroundColor = 'var(--bg-card-subtle)';
                            e.currentTarget.style.borderColor = 'var(--border-subtle)';
                          }}
                        >
                          <span>{getSourceButtonLabel(src.platform)}</span>
                          <ExternalLink size={12} />
                        </a>
                      ) : null}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

const actionBtnStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '4px',
  background: 'none',
  border: '1px solid var(--border-subtle)',
  borderRadius: '6px',
  padding: '4px 8px',
  fontSize: '0.75rem',
  color: 'var(--text-muted)',
  cursor: 'pointer',
  backgroundColor: 'var(--bg-card)'
};

