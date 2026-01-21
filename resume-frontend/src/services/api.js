const API_BASE = '';

// Token management
export function getAccessToken() {
  return localStorage.getItem('access_token');
}

export function getRefreshToken() {
  return localStorage.getItem('refresh_token');
}

export function setTokens(access, refresh) {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
}

export function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

// Auth API
export async function login(username, password) {
  const res = await fetch(`${API_BASE}/api/token/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await res.json();
  if (res.ok) {
    setTokens(data.access, data.refresh);
  }
  return { ok: res.ok, data };
}

export async function register(username, password) {
  const res = await fetch(`${API_BASE}/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  return { ok: res.ok, data: await res.json() };
}

export async function refreshToken() {
  const refresh = getRefreshToken();
  if (!refresh) return false;

  const res = await fetch(`${API_BASE}/api/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh })
  });

  if (res.ok) {
    const data = await res.json();
    localStorage.setItem('access_token', data.access);
    return true;
  }
  clearTokens();
  return false;
}

// Authenticated fetch wrapper
async function authFetch(url, options = {}) {
  let token = getAccessToken();

  const doFetch = (t) => fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${t}`,
      'Content-Type': 'application/json'
    }
  });

  let res = await doFetch(token);

  // If 401, try refresh
  if (res.status === 401) {
    const refreshed = await refreshToken();
    if (refreshed) {
      token = getAccessToken();
      res = await doFetch(token);
    }
  }

  return res;
}

// Resume API
export async function fetchResumeData() {
  const res = await authFetch(`${API_BASE}/resume/get_data/`);
  if (!res.ok) return null;
  const json = await res.json();
  return json.data;
}

export async function saveResumeData(data) {
  const res = await authFetch(`${API_BASE}/resume/get_data/`, {
    method: 'POST',
    body: JSON.stringify({ data })
  });
  return res.ok;
}

export async function generatePdfFromJson(jsonData, templateName = 'harward_style', cssName = 'harward', paymentId = null) {
  const res = await authFetch(`${API_BASE}/resume/get_pdf_from_json/`, {
    method: 'POST',
    body: JSON.stringify({
      json_input: JSON.stringify(jsonData),
      template_name: templateName,
      css_name: cssName,
      payment_id: paymentId
    })
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ error: 'PDF generation failed' }));
    throw new Error(error.error || 'PDF generation failed');
  }
  return await res.blob();
}

export function isAuthenticated() {
  return !!getAccessToken();
}
