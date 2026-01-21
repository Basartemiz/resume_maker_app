import { getAccessToken, refreshToken } from '../services/api';

const API_BASE = '';

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

  if (res.status === 401) {
    const refreshed = await refreshToken();
    if (refreshed) {
      token = getAccessToken();
      res = await doFetch(token);
    }
  }

  return res;
}

export async function getPaymentConfig() {
  const res = await authFetch(`${API_BASE}/payment/config/`);
  if (!res.ok) return null;
  return await res.json();
}

export async function createPaymentIntent() {
  const res = await authFetch(`${API_BASE}/payment/create-intent/`, {
    method: 'POST',
    body: JSON.stringify({})
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to create payment intent');
  }
  return await res.json();
}

export async function verifyPayment(paymentId) {
  const res = await authFetch(`${API_BASE}/payment/verify/`, {
    method: 'POST',
    body: JSON.stringify({ payment_id: paymentId })
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Payment verification failed');
  }
  return await res.json();
}
