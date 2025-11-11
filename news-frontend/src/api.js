// src/api.js
import axios from 'axios';

// Configure API base URL (dev fallback to 127.0.0.1 avoids IPv6 quirks)
const API_BASE = process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000';

// Single axios instance
const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

// Attach Authorization header if a token exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401s from auth-protected endpoints
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    const url = error?.config?.url || '';
    if (
      status === 401 &&
      (url.startsWith('/users/me') || url.startsWith('/admin') || url.startsWith('/auth'))
    ) {
      try {
        localStorage.removeItem('token');
        localStorage.removeItem('user_email');
      } catch (_) {}
      // Redirect to login
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

/*
  Auth endpoints
  Ensure JSON body always matches FastAPI models to avoid 422.
*/
export const registerUser = async (data) => {
  // data must be { name?, email, password }
  return api.post('/auth/register', data);
};

export const loginUser = async (email, password) => {
  // Always send JSON, not separate args; this fixes 422.
  return api.post('/auth/login', { email, password });
};

// Optional: OAuth2 form flow if you expose /auth/token with OAuth2PasswordRequestForm
export const loginWithForm = async (email, password) => {
  const form = new URLSearchParams();
  form.append('username', email);
  form.append('password', password);
  return api.post('/auth/token', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
};

export const getCurrentUser = async () => {
  const res = await api.get('/users/me');
  return res.data;
};

/*
  Admin endpoints (require Bearer token)
*/
export const getAdminUsers = async () => {
  const res = await api.get('/admin/users');
  return res.data;
};

export const getAdminStats = async () => {
  const res = await api.get('/admin/dashboard');
  return res.data;
};

export const deleteAdminUser = async (userId) => {
  const res = await api.delete(`/admin/users/${userId}`);
  return res.data;
};

// Forgot/Reset password flows

// Start forgot-password flow (e.g., send reset link/OTP)
export const forgotPassword = async (email) => {
  // Backend expects { email }
  return api.post('/auth/forgot-password', { email });
};

// Complete reset-password flow
export const resetPassword = async ({ token, password }) => {
  // If your backend uses a token in query instead of body, adapt accordingly:
  // return api.post(`/auth/reset-password?token=${encodeURIComponent(token)}`, { password });
  return api.post('/auth/reset-password', { token, password });
};


/*
  Example content endpoints (keep as needed)
*/
export const getNews = async (query = 'technology') => {
  const res = await api.get(`/news`, { params: { query } });
  return res.data;
};

export const getRecentArticles = async () => {
  const res = await api.get('/recent-articles');
  return res.data;
};

export const detectTrends = async (range = '7d') => {
  const res = await api.get('/detect-trends/topics', { params: { range } });
  return res.data;
};

// Export axios instance for rare custom calls
export default api;
