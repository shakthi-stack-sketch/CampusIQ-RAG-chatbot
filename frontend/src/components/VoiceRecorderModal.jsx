import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Check, X, Loader2, Sparkles } from 'lucide-react';
import { transcribeAudio } from '../services/api';

export default function VoiceRecorderModal({ isOpen, onClose, onApplyTranscript }) {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recognitionRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      setTranscript('');
      setError('');
      startListening();
    } else {
      stopListening();
    }
    return () => {
      stopListening();
    };
  }, [isOpen]);

  const startListening = async () => {
    setError('');
    setTranscript('');

    // Try browser SpeechRecognition first for real-time live preview
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event) => {
        let fullTranscript = '';
        for (let i = 0; i < event.results.length; i++) {
          fullTranscript += event.results[i][0].transcript + ' ';
        }
        setTranscript(fullTranscript.trim());
      };

      recognition.onerror = (err) => {
        console.warn('SpeechRecognition error:', err);
      };

      recognitionRef.current = recognition;
      try {
        recognition.start();
      } catch (e) {
        console.warn('Recognition start error:', e);
      }
    }

    // Also record audio blob for local Whisper backend fallback
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      audioChunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());
        // If real-time recognition didn't catch text, try local Whisper backend
        if (!transcript.trim() && audioChunksRef.current.length > 0) {
          setIsProcessing(true);
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          try {
            const res = await transcribeAudio(audioBlob, 'question.webm');
            if (res.success && res.text) {
              setTranscript(res.text);
            }
          } catch (e) {
            console.warn('Whisper backend transcription failed:', e);
          } finally {
            setIsProcessing(false);
          }
        }
      };

      recorder.start();
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
    } catch (err) {
      console.warn('Mic access error:', err);
      setError('Microphone access denied or unavailable. Please type your question directly.');
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {}
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
  };

  const handleApply = () => {
    stopListening();
    if (transcript.trim()) {
      onApplyTranscript(transcript.trim());
    }
    onClose();
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
          maxWidth: '480px',
          backgroundColor: 'var(--bg-card)',
          borderRadius: 'var(--radius-lg)',
          border: '1.5px solid var(--border-subtle)',
          boxShadow: 'var(--shadow-lg)',
          padding: '28px 24px',
          textAlign: 'center',
          position: 'relative'
        }}
      >
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '16px',
            right: '16px',
            background: 'none',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer'
          }}
        >
          <X size={18} />
        </button>

        {/* Pulse Recording Visualizer */}
        <div style={{ position: 'relative', display: 'inline-block', margin: '14px 0 20px 0' }}>
          {isRecording && (
            <div
              style={{
                position: 'absolute',
                inset: '-12px',
                borderRadius: '50%',
                backgroundColor: 'var(--accent-burgundy)',
                opacity: 0.25,
                animation: 'pulseSubtle 1.4s ease-out infinite'
              }}
            />
          )}
          <div
            onClick={isRecording ? stopListening : startListening}
            style={{
              position: 'relative',
              width: '68px',
              height: '68px',
              borderRadius: '50%',
              backgroundColor: isRecording ? 'var(--accent-burgundy)' : 'var(--bg-secondary)',
              color: isRecording ? '#FFFFFF' : 'var(--text-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto',
              cursor: 'pointer',
              boxShadow: 'var(--shadow-md)',
              transition: 'all 0.2s ease'
            }}
          >
            {isRecording ? <Mic size={28} /> : <MicOff size={28} />}
          </div>
        </div>

        <h3 style={{
          fontFamily: 'var(--font-serif)',
          fontSize: '1.25rem',
          color: 'var(--accent-burgundy)',
          marginBottom: '6px'
        }}>
          {isRecording ? 'Listening to your college query...' : 'Voice Recording Stopped'}
        </h3>

        <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
          {isRecording
            ? 'Speak clearly about mess menus, academics, dress code, clubs, or campus events.'
            : 'Click the microphone above to start speaking again.'}
        </p>

        {/* Transcript Box */}
        <div style={{
          minHeight: '84px',
          maxHeight: '140px',
          overflowY: 'auto',
          backgroundColor: 'var(--bg-card-subtle)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '12px 14px',
          fontSize: '0.92rem',
          color: transcript ? 'var(--text-primary)' : 'var(--text-muted)',
          textAlign: 'left',
          marginBottom: '20px',
          lineHeight: 1.5
        }}>
          {isProcessing ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-burgundy)' }}>
              <Loader2 size={16} className="animate-spin" />
              <span>Whisper speech-to-text processing...</span>
            </div>
          ) : (
            transcript || (isRecording ? 'Waiting for speech...' : 'No speech recognized yet.')
          )}
        </div>

        {error && (
          <div style={{ color: '#C0392B', fontSize: '0.8rem', marginBottom: '14px' }}>
            {error}
          </div>
        )}

        {/* Modal Actions */}
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
          <button
            onClick={onClose}
            style={{
              padding: '8px 16px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              backgroundColor: 'transparent',
              color: 'var(--text-secondary)',
              fontSize: '0.84rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Cancel
          </button>

          <button
            onClick={handleApply}
            disabled={!transcript.trim()}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 18px',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              backgroundColor: transcript.trim() ? 'var(--accent-burgundy)' : 'var(--border-subtle)',
              color: '#FFFFFF',
              fontSize: '0.84rem',
              fontWeight: 600,
              cursor: transcript.trim() ? 'pointer' : 'default',
              boxShadow: 'var(--shadow-sm)'
            }}
          >
            <Check size={14} />
            <span>Use Question</span>
          </button>
        </div>
      </div>
    </div>
  );
}
