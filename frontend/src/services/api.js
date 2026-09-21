/**
 * API Service for communicating with CampusIQ FastAPI Backend
 */

const API_BASE = '/api';

// ==========================================
// AUTHENTICATION & TOKEN STORAGE
// ==========================================

export function getAuthToken() {
  return localStorage.getItem('campusiq_jwt_token');
}

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem('campusiq_jwt_token', token);
  } else {
    localStorage.removeItem('campusiq_jwt_token');
  }
}

export function getStoredUser() {
  try {
    const raw = localStorage.getItem('campusiq_auth_user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setStoredUser(user) {
  if (user) {
    localStorage.setItem('campusiq_auth_user', JSON.stringify(user));
    if (user.id) {
      setStoredUserId(user.id);
    }
  } else {
    localStorage.removeItem('campusiq_auth_user');
  }
}

export function logoutUser() {
  localStorage.removeItem('campusiq_jwt_token');
  localStorage.removeItem('campusiq_auth_user');
}

export function isAuthenticated() {
  return !!getAuthToken();
}

export function getAuthHeaders(customHeaders = {}) {
  const headers = { ...customHeaders };
  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const uid = getStoredUserId();
  if (uid) {
    headers['X-User-Id'] = uid;
  }
  return headers;
}

// User Profile & Fallback ID
export function getStoredUserId() {
  let uid = localStorage.getItem('campusiq_user_id');
  if (!uid) {
    uid = `guest_${Math.random().toString(36).substring(2, 9)}`;
    localStorage.setItem('campusiq_user_id', uid);
  }
  return uid;
}

export function setStoredUserId(newId) {
  if (newId && newId.trim()) {
    localStorage.setItem('campusiq_user_id', newId.trim());
  }
}

// ==========================================
// AUTH API ENDPOINTS
// ==========================================

export async function signupUser(payload) {
  const res = await fetch(`${API_BASE}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Signup failed. Please verify your details.');
  }
  if (data.access_token) {
    setAuthToken(data.access_token);
    setStoredUser(data.user);
  }
  return data;
}

export async function loginUser(payload) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Invalid email or password.');
  }
  if (data.access_token) {
    setAuthToken(data.access_token);
    setStoredUser(data.user);
  }
  return data;
}

export async function getMe() {
  const token = getAuthToken();
  if (!token) return null;
  try {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      if (res.status === 401) {
        logoutUser();
      }
      return null;
    }
    const user = await res.json();
    setStoredUser(user);
    return user;
  } catch {
    return null;
  }
}

export async function updateUserProfile(profileData) {
  const res = await fetch(`${API_BASE}/auth/profile`, {
    method: 'PUT',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(profileData)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to update profile');
  }
  const user = await res.json();
  setStoredUser(user);
  return user;
}

export async function forgotPasswordApi(email) {
  const res = await fetch(`${API_BASE}/auth/forgot-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to submit password recovery request.');
  }
  return data;
}

// ==========================================
// CHAT & CONVERSATIONS
// ==========================================

export async function sendMessage(payload) {
  const headers = getAuthHeaders({ 'Content-Type': 'application/json' });
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers,
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
  const res = await fetch(url, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error('Failed to load conversations');
  return res.json();
}

export async function getConversation(convId) {
  const res = await fetch(`${API_BASE}/conversations/${convId}`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error('Failed to load conversation details');
  return res.json();
}

export async function createConversation(title = 'New Conversation') {
  const res = await fetch(`${API_BASE}/conversations`, {
    method: 'POST',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error('Failed to create conversation');
  return res.json();
}

export async function renameConversation(convId, title) {
  const res = await fetch(`${API_BASE}/conversations/${convId}`, {
    method: 'PATCH',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error('Failed to rename conversation');
  return res.json();
}

export async function deleteConversation(convId) {
  const res = await fetch(`${API_BASE}/conversations/${convId}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
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

// ==========================================
// SAVED ANSWERS (PROTECTED)
// ==========================================

export async function getSavedAnswers() {
  const uid = getStoredUserId();
  const res = await fetch(`${API_BASE}/saved?user_id=${encodeURIComponent(uid)}`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    if (res.status === 401) {
      throw new Error('SIGN_IN_REQUIRED');
    }
    throw new Error('Failed to load saved answers');
  }
  return res.json();
}

export async function saveAnswerApi(payload) {
  const uid = getStoredUserId();
  const res = await fetch(`${API_BASE}/saved`, {
    method: 'POST',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ ...payload, user_id: uid })
  });
  if (!res.ok) {
    if (res.status === 401) {
      throw new Error('SIGN_IN_REQUIRED');
    }
    throw new Error('Failed to save answer');
  }
  return res.json();
}

export async function unsaveAnswerApi(savedId) {
  const uid = getStoredUserId();
  const res = await fetch(`${API_BASE}/saved/${savedId}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    if (res.status === 401) {
      throw new Error('SIGN_IN_REQUIRED');
    }
    throw new Error('Failed to unsave answer');
  }
  return res.json();
}

export async function unsaveByMessageIdApi(messageId) {
  const uid = getStoredUserId();
  const res = await fetch(`${API_BASE}/saved/by-message/${messageId}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    if (res.status === 401) {
      throw new Error('SIGN_IN_REQUIRED');
    }
    throw new Error('Failed to unsave answer');
  }
  return res.json();
}

// ==========================================
// CAMPUS PULSE & OPPORTUNITIES (PUBLIC)
// ==========================================

export async function getCampusPulse(category = null, search = '') {
  const params = new URLSearchParams();
  if (category && category !== 'all') params.append('category', category);
  if (search) params.append('search', search);
  const url = `${API_BASE}/pulse${params.toString() ? '?' + params.toString() : ''}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to load campus pulse');
  return res.json();
}

export async function getVerifiedOpportunities(category = null) {
  const params = new URLSearchParams();
  if (category && category !== 'all') params.append('category', category);
  const url = `${API_BASE}/opportunities${params.toString() ? '?' + params.toString() : ''}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to load opportunities');
  return res.json();
}

export async function getVerifiedLocations() {
  const res = await fetch(`${API_BASE}/locations`);
  if (!res.ok) throw new Error('Failed to load campus locations');
  return res.json();
}

// ==========================================
// PERSONAL KNOWLEDGE VAULT (PROTECTED)
// ==========================================

export async function getVaultDocuments() {
  const res = await fetch(`${API_BASE}/vault/documents`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    if (res.status === 401) {
      throw new Error('SIGN_IN_REQUIRED');
    }
    throw new Error('Failed to load personal vault documents');
  }
  return res.json();
}

export async function uploadVaultDocument(file) {
  const uid = getStoredUserId();
  const formData = new FormData();
  formData.append('file', file);
  formData.append('user_id', uid);

  const res = await fetch(`${API_BASE}/vault/upload`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData
  });
  if (!res.ok) {
    if (res.status === 401) {
      throw new Error('SIGN_IN_REQUIRED');
    }
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to upload personal document');
  }
  return res.json();
}

export async function deleteVaultDocument(docId) {
  const res = await fetch(`${API_BASE}/vault/documents/${docId}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    if (res.status === 401) {
      throw new Error('SIGN_IN_REQUIRED');
    }
    throw new Error('Failed to delete personal document');
  }
  return res.json();
}

export async function queryPersonalVault(query) {
  const uid = getStoredUserId();
  const res = await fetch(`${API_BASE}/vault/query`, {
    method: 'POST',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ query, user_id: uid })
  });
  if (!res.ok) {
    if (res.status === 401) {
      throw new Error('SIGN_IN_REQUIRED');
    }
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to query personal vault');
  }
  return res.json();
}
