/**
 * API Service for communicating with CampusIQ FastAPI Backend
 */

const API_BASE = '/api';

export async function sendMessage(payload) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to generate answer');
  }
  return res.json();
}

export async function getConversations(search = '') {
  const url = search ? `${API_BASE}/conversations?search=${encodeURIComponent(search)}` : `${API_BASE}/conversations`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to load conversations');
  return res.json();
}

export async function getConversation(convId) {
  const res = await fetch(`${API_BASE}/conversations/${convId}`);
  if (!res.ok) throw new Error('Failed to load conversation details');
  return res.json();
}

export async function createConversation(title = 'New Conversation') {
  const res = await fetch(`${API_BASE}/conversations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error('Failed to create conversation');
  return res.json();
}

export async function renameConversation(convId, title) {
  const res = await fetch(`${API_BASE}/conversations/${convId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error('Failed to rename conversation');
  return res.json();
}

export async function deleteConversation(convId) {
  const res = await fetch(`${API_BASE}/conversations/${convId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete conversation');
  return res.json();
}

export async function transcribeAudio(audioBlob, filename = 'speech.webm') {
  const formData = new FormData();
  formData.append('file', audioBlob, filename);

  const res = await fetch(`${API_BASE}/voice/transcribe`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Audio transcription failed');
  return res.json();
}

export async function getKnowledgeStatus() {
  const res = await fetch(`${API_BASE}/knowledge/status`);
  if (!res.ok) throw new Error('Failed to get knowledge status');
  return res.json();
}

export async function syncKnowledge() {
  const res = await fetch(`${API_BASE}/knowledge/sync`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to sync knowledge base');
  return res.json();
}
