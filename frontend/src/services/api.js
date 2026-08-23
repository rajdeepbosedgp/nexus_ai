const BASE_URL = import.meta.env.VITE_API_URL || '';
const API_BASE = `${BASE_URL}/api`;

export function getAuthHeaders() {
  const token = localStorage.getItem('nexus_token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

export async function request(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeaders(),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Network request failed' }));
    throw new Error(errorData.detail || `HTTP Error ${response.status}`);
  }

  return response.json();
}

// --- Auth APIs ---
export const authApi = {
  login: (email, password) => request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  }),
  register: (data) => request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  getMe: () => request('/auth/me'),
};

// --- Complaints APIs ---
export const complaintsApi = {
  list: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/complaints${query ? `?${query}` : ''}`);
  },
  create: (data) => request('/complaints', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  uploadPhoto: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${API_BASE}/complaints/upload`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData,
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Photo upload failed' }));
      throw new Error(err.detail || 'Photo upload failed');
    }
    return response.json();
  },
  updateStatus: (id, status, note) => request(`/complaints/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status, note }),
  }),
  updatePriority: (id, priority) => request(`/complaints/${id}/priority?priority=${priority}`, {
    method: 'PATCH',
  }),
};

// --- Notices APIs ---
export const noticesApi = {
  list: () => request('/notices'),
  create: (data) => request('/notices', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
};

// --- Patterns APIs ---
export const patternsApi = {
  list: () => request('/patterns'),
  getDetail: (id) => request(`/patterns/${id}`),
  detect: () => request('/patterns/detect', { method: 'POST' }),
};

// --- Dashboard APIs ---
export const dashboardApi = {
  getMetrics: () => request('/dashboard'),
};
