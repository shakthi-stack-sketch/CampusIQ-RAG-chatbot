import React, { useState, useEffect, useRef } from 'react';
import { X, FolderLock, Upload, Trash2, FileText, Send, ShieldAlert, Sparkles } from 'lucide-react';
import { getVaultDocuments, uploadVaultDocument, deleteVaultDocument, queryPersonalVault, getStoredUserId, setStoredUserId } from '../services/api';

export default function PersonalVaultModal({ isOpen, onClose }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [queryText, setQueryText] = useState('');
  const [queryLoading, setQueryLoading] = useState(false);
  const [vaultChatHistory, setVaultChatHistory] = useState([]);
  const [customUserId, setCustomUserId] = useState(() => getStoredUserId());
  const [isEditingUser, setIsEditingUser] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      loadDocs();
    }
  }, [isOpen]);

  const loadDocs = async () => {
    setLoading(true);
    try {
      const docs = await getVaultDocuments();
      setDocuments(docs || []);
    } catch (e) {
      console.warn('Failed to load vault documents:', e);
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await uploadVaultDocument(file);
      await loadDocs();
    } catch (err) {
      alert(err.message || 'Failed to upload document');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (docId) => {
    if (!window.confirm('Delete this personal document?')) return;
    try {
      await deleteVaultDocument(docId);
      setDocuments(prev => prev.filter(d => d.id !== docId));
    } catch (e) {
      console.warn('Failed to delete vault document:', e);
    }
  };

  const handleVaultQuery = async (e) => {
    e?.preventDefault();
    const q = queryText.trim();
    if (!q || queryLoading) return;

    setQueryLoading(true);
    setQueryText('');
    const userQ = { role: 'user', content: q };
    setVaultChatHistory(prev => [...prev, userQ]);

    try {
      const res = await queryPersonalVault(q);
      setVaultChatHistory(prev => [...prev, {
        role: 'vault_assistant',
        content: res.answer,
        sources: res.sources || []
      }]);
    } catch (err) {
      setVaultChatHistory(prev => [...prev, {
        role: 'vault_assistant',
        content: err.message || 'Failed to query personal vault',
        sources: []
      }]);
    } finally {
      setQueryLoading(false);
    }
  };

  const handleSaveUserId = () => {
    if (customUserId.trim()) {
      setStoredUserId(customUserId.trim());
      setIsEditingUser(false);
      loadDocs();
      setVaultChatHistory([]);
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
          maxWidth: '780px',
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
          padding: '18px 24px 14px 24px',
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
              <FolderLock size={22} />
            </div>
            <div>
              <h3 style={{
                fontFamily: 'var(--font-display)',
                fontSize: '1.24rem',
                fontWeight: 700,
                color: 'var(--accent-burgundy)',
                margin: 0
              }}>
                Personal Knowledge Vault
              </h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0 }}>
                Upload personal study material (timetable, notes, syllabus). Strictly isolated from official college knowledge.
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

        {/* User Isolation Badge Bar */}
        <div style={{
          padding: '8px 24px',
          backgroundColor: 'var(--bg-card-subtle)',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '0.76rem',
          color: 'var(--text-muted)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Vault User:</span>
            {isEditingUser ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <input
                  type="text"
                  value={customUserId}
                  onChange={(e) => setCustomUserId(e.target.value)}
                  style={{
                    padding: '2px 6px',
                    fontSize: '0.76rem',
                    borderRadius: '4px',
                    border: '1px solid var(--accent-burgundy)',
                    backgroundColor: 'var(--bg-card)',
                    color: 'var(--text-primary)',
                    outline: 'none'
                  }}
                />
                <button onClick={handleSaveUserId} style={{ cursor: 'pointer', color: 'var(--accent-burgundy)', fontWeight: 600 }}>Save</button>
              </div>
            ) : (
              <span
                onClick={() => setIsEditingUser(true)}
                style={{
                  cursor: 'pointer',
                  textDecoration: 'underline',
                  fontWeight: 600,
                  color: 'var(--accent-burgundy)'
                }}
                title="Click to change vault user ID"
              >
                {customUserId}
              </span>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#27AE60' }}>
            <ShieldAlert size={12} />
            <span>Partitioned & Encrypted Session</span>
          </div>
        </div>

        {/* Body Split View */}
        <div style={{ flex: 1, display: 'flex', overflow: 'hidden', minHeight: 0 }}>
          {/* Left: Document List & Upload */}
          <div style={{
            width: '42%',
            borderRight: '1px solid var(--border-subtle)',
            display: 'flex',
            flexDirection: 'column',
            padding: '16px',
            backgroundColor: 'var(--bg-card-subtle)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ fontSize: '0.78rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                My Documents ({documents.length})
              </span>

              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '5px',
                  padding: '5px 10px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--accent-burgundy)',
                  color: '#FFFFFF',
                  border: 'none',
                  fontSize: '0.76rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                <Upload size={12} />
                <span>{uploading ? 'Uploading...' : 'Upload File'}</span>
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt,.pdf,.docx,.doc"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
              />
            </div>

            <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {loading ? (
                <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  Loading documents...
                </div>
              ) : documents.length === 0 ? (
                <div style={{
                  textAlign: 'center',
                  padding: '30px 10px',
                  color: 'var(--text-muted)',
                  fontSize: '0.84rem'
                }}>
                  <FileText size={28} style={{ opacity: 0.3, marginBottom: '8px' }} />
                  <div>No personal documents uploaded yet.</div>
                  <div style={{ fontSize: '0.74rem', marginTop: '4px', opacity: 0.7 }}>
                    Upload your syllabus, notes, or timetable (.pdf, .docx, .txt).
                  </div>
                </div>
              ) : (
                documents.map(doc => (
                  <div
                    key={doc.id}
                    style={{
                      padding: '8px 10px',
                      backgroundColor: 'var(--bg-card)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: '6px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      fontSize: '0.80rem'
                    }}
                  >
                    <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '80%' }}>
                      <div style={{ fontWeight: 600, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {doc.filename}
                      </div>
                      <div style={{ fontSize: '0.70rem', color: 'var(--text-muted)' }}>
                        {(doc.file_size / 1024).toFixed(1)} KB • {doc.file_type.toUpperCase()}
                      </div>
                    </div>

                    <button
                      onClick={() => handleDelete(doc.id)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--text-muted)',
                        cursor: 'pointer',
                        padding: '4px'
                      }}
                      title="Delete document"
                    >
                      <Trash2 size={13} color="#E74C3C" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Right: Personal Vault Query Console */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '16px' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.78rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              color: 'var(--accent-burgundy)',
              marginBottom: '10px'
            }}>
              <Sparkles size={14} />
              <span>Ask Questions About My Documents</span>
            </div>

            {/* Q&A Stream */}
            <div style={{
              flex: 1,
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              gap: '10px',
              paddingRight: '6px'
            }}>
              {vaultChatHistory.length === 0 ? (
                <div style={{
                  textAlign: 'center',
                  padding: '40px 15px',
                  color: 'var(--text-muted)',
                  fontSize: '0.84rem'
                }}>
                  Ask specific questions about your uploaded notes, timetable, or syllabus.<br />
                  Answers are grounded strictly in your personal vault.
                </div>
              ) : (
                vaultChatHistory.map((m, idx) => (
                  <div
                    key={idx}
                    style={{
                      alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
                      maxWidth: '88%',
                      padding: '8px 12px',
                      borderRadius: '8px',
                      backgroundColor: m.role === 'user' ? 'var(--accent-burgundy-light)' : 'var(--bg-card-subtle)',
                      border: '1px solid var(--border-subtle)',
                      fontSize: '0.84rem',
                      color: 'var(--text-primary)',
                      lineHeight: 1.45,
                      whiteSpace: 'pre-wrap'
                    }}
                  >
                    <div style={{
                      fontSize: '0.70rem',
                      fontWeight: 700,
                      color: m.role === 'user' ? 'var(--accent-burgundy)' : 'var(--accent-gold)',
                      marginBottom: '2px'
                    }}>
                      {m.role === 'user' ? 'You' : 'Vault Assistant'}
                    </div>
                    {m.content}
                  </div>
                ))
              )}
              {queryLoading && (
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                  Reading your personal documents...
                </div>
              )}
            </div>

            {/* Input Composer */}
            <form onSubmit={handleVaultQuery} style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
              <input
                type="text"
                value={queryText}
                onChange={(e) => setQueryText(e.target.value)}
                placeholder="Ask about your timetable, notes, or syllabus..."
                disabled={queryLoading}
                style={{
                  flex: 1,
                  padding: '8px 12px',
                  fontSize: '0.84rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border-subtle)',
                  backgroundColor: 'var(--bg-card)',
                  color: 'var(--text-primary)',
                  outline: 'none'
                }}
              />
              <button
                type="submit"
                disabled={!queryText.trim() || queryLoading}
                style={{
                  padding: '8px 14px',
                  borderRadius: '6px',
                  backgroundColor: queryText.trim() && !queryLoading ? 'var(--accent-burgundy)' : 'var(--border-subtle)',
                  color: '#FFFFFF',
                  border: 'none',
                  cursor: queryText.trim() && !queryLoading ? 'pointer' : 'default',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <Send size={14} />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
