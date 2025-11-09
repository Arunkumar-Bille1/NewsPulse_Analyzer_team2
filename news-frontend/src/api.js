//import axios from 'axios';
//
//const API_BASE_URL = 'http://localhost:8000';
//
//const api = axios.create({
//  baseURL: API_BASE_URL,
//  timeout: 10000,
//});
//
//// Add token to requests automatically
//api.interceptors.request.use((config) => {
//  const token = localStorage.getItem('token');
//  if (token) {
//    config.headers.Authorization = `Bearer ${token}`;
//  }
//  return config;
//});
//
//// Handle 401 errors globally
//api.interceptors.response.use(
//  (response) => response,
//  (error) => {
//    if (error.response?.status === 401) {
//      localStorage.removeItem('token');
//      localStorage.removeItem('user_email');
//      window.location.href = '/login';
//    }
//    return Promise.reject(error);
//  }
//);
//
//
//export const registerUser = async (userData) => {
//  try {
//    const response = await api.post('/register', userData);
//    return response;
//  } catch (error) {
//    throw error;
//  }
//};
//
//// Login user
//export const loginUser = async (email, password) => {
//  try {
//    const response = await api.post('/login', { email, password });
//    return response;
//  } catch (error) {
//    throw error;
//  }
//};
//
//
//// Get current user
//export const getCurrentUser = async () => {
//  try {
//    const response = await api.get('/users/me');
//    return response.data;
//  } catch (error) {
//    throw error;
//  }
//};
//
//// Get news with query
//export const getNews = async (query = 'technology') => {
//  try {
//    const response = await api.get(`/news?query=${encodeURIComponent(query)}`);
//    return response.data;
//  } catch (error) {
//    throw error;
//  }
//};
//
//// Get stored news
//export const getStoredNews = async () => {
//  try {
//    const response = await api.get('/stored-news');
//    return response.data;
//  } catch (error) {
//    throw error;
//  }
//};
//
//// Test connection
//export const testConnection = async () => {
//  try {
//    const response = await api.get('/');
//    return response;
//  } catch (error) {
//    throw error;
//  }
//};
//
//// Forgot password
//export const forgotPassword = async (email) => {
//  try {
//    const response = await api.post('/forgot-password', { email });
//    return response;
//  } catch (error) {
//    throw error;
//  }
//};
//
//// Reset password
//export const resetPassword = async (token, newPassword) => {
//  try {
//    const response = await api.post('/reset-password', {
//      token,
//      new_password: newPassword
//    });
//    return response;
//  } catch (error) {
//    throw error;
//  }
//};
//
//// Get profile
//export const getProfile = async () => {
//  try {
//    const response = await api.get('/profile');
//    return response;
//  } catch (error) {
//    throw error;
//  }
//};
//
//// Update profile
//export const updateProfile = async (profileData) => {
//  try {
//    const response = await api.put('/profile', profileData);
//    return response;
//  } catch (error) {
//    throw error;
//  }
//};
//
//export default api;


// src/api.js
import axios from "axios";

// Single source of truth for API base (override via frontend .env)
const API_BASE = process.env.REACT_APP_API_BASE || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

// 1) Always attach the latest token to every request
api.interceptors.request.use((config) => {
  const tok = localStorage.getItem("token");
  if (tok) config.headers.Authorization = `Bearer ${tok}`;
  console.log("Auth header set for", config.url, !!tok);
  return config;
});

// 2) Only force logout on auth-check endpoints (/users/me, /auth/*)
//    Admin endpoints (/admin/*) will surface errors in the UI instead of clearing the session
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const url = err?.config?.url || "";
    if (err?.response?.status === 401 && (url.startsWith("/users/me") || url.startsWith("/auth"))) {
      localStorage.removeItem("token");
      localStorage.removeItem("user_email");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

/* =========================
   Convenience API helpers
   ========================= */

// Auth
export const registerUser = (userData) => api.post("/auth/register", userData);
export const loginUser = (email, password) => api.post("/auth/login", { email, password });

// (Optional endpoints; include only if implemented on backend)
export const forgotPassword = (email) => api.post("/auth/forgot-password", { email });
export const resetPassword = (token, newPassword) =>
  api.post("/auth/reset-password", { token, new_password: newPassword });

// User
export const getCurrentUser = async () => (await api.get("/users/me")).data;

// News
export const getNews = async (query = "technology") =>
  (await api.get(`/news`, { params: { query } })).data;
export const getStoredNews = async () => (await api.get("/news_stored")).data;

// Profile
export const getProfile = () => api.get("/profile");
export const updateProfile = (profileData) => api.put("/profile", profileData);

// Admin (now available for the dashboard UI)
export const getAdminUsers = async () => (await api.get("/admin/users")).data;
export const getAdminStats = async () => (await api.get("/admin/dashboard")).data;
export const deleteAdminUser = (userId) => api.delete(`/admin/users/${userId}`);

export const testConnection = () => api.get("/");
export default api;
