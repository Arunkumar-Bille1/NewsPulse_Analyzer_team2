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
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user_email');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth
export const registerUser = async (userData) => api.post('/auth/register', userData);
export const loginUser = async (email, password) => api.post('/auth/login', { email, password });
export const forgotPassword = async (email) => api.post('/auth/forgot-password', { email });
export const resetPassword = async (token, newPassword) =>
  api.post('/auth/reset-password', { token, new_password: newPassword });

// User
export const getCurrentUser = async () => api.get('/users/me').then(r => r.data);

// News
export const getNews = async (query = 'technology') =>
  api.get(`/news?query=${encodeURIComponent(query)}`).then(r => r.data);

export const getStoredNews = async () =>
  api.get('/news_stored').then(r => r.data); // note: path changed

// Profile
export const getProfile = async () => api.get('/profile');
export const updateProfile = async (profileData) => api.put('/profile', profileData);

export const testConnection = async () => api.get('/');
export default api;
