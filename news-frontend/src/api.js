import axios from "axios";

const API_BASE = process.env.REACT_APP_API_BASE || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 20000,
});

// ------------------------------------------------------
// ⭐ INTERCEPTORS
// ------------------------------------------------------
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (error) => {
    const status = error?.response?.status || 0;

    // Auto logout if unauthorized
    if (status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user_email");
      window.location.href = "/login";
    }

    return Promise.reject(error);
  }
);

export default api;

// ------------------------------------------------------
// 🔐 AUTH
// ------------------------------------------------------
export const registerUser = (data) => api.post("/auth/register", data);

export const loginUser = (email, password) =>
  api.post("/auth/login", { email, password });

export const getCurrentUser = async () =>
  (await api.get("/users/me")).data;

export const forgotPassword = (email) =>
  api.post("/auth/forgot-password", { email });

export const resetPassword = (token, password) =>
  api.post("/auth/reset-password", {
    token,
    new_password: password,
  });

// ------------------------------------------------------
// 🧩 ADMIN
// ------------------------------------------------------
export const getAdminUsers = async () =>
  (await api.get("/admin/users")).data;

export const getAdminStats = async () =>
  (await api.get("/admin/dashboard")).data;

export const deleteAdminUser = async (id) =>
  (await api.delete(`/admin/users/${id}`)).data;

export const getSystemStatus = async () =>
  (await api.get("/admin/system_status")).data;

export const getInsights = async () =>
  (await api.get("/admin/insights")).data;

// ------------------------------------------------------
// 📰 NEWS
// ------------------------------------------------------
export const searchArticles = async (query) =>
  (await api.get("/news", { params: { query } })).data;

export const getTrendingArticles = async () =>
  (await api.get("/news", { params: { query: "trending" } })).data;

export const getCategoryArticles = async (category) =>
  (await api.get("/news", { params: { query: category } })).data;

export const getArticleDetails = async (url) =>
  (await api.get("/article/details", { params: { url } })).data;

// ------------------------------------------------------
// 🔥 TREND DETECTION
// ------------------------------------------------------
export const detectTrends = async (range = "7d") =>
  (await api.get("/detect-trends/topics", { params: { range } })).data;

// ------------------------------------------------------
// ⭐ BOOKMARK API – FINAL FIXED VERSION
// ------------------------------------------------------

// Add bookmark
export const addBookmark = (user_id, article) =>
  api.post("/bookmarks/add", { user_id, article });

// Remove bookmark
export const removeBookmark = (user_id, article_url) =>
  api.delete("/bookmarks/remove", {
    data: { user_id, article_url },
  });

// Get all bookmarks
export const getBookmarks = (user_id) =>
  api.get(`/bookmarks/${user_id}`);

// Check bookmark (NO LOOP ⚠️)
export const checkBookmark = (user_id, article_url) =>
  api.post("/bookmarks/check", { user_id, article_url });

// ------------------------------------------------------
// 🔍 COMPARE ARTICLES
// ------------------------------------------------------
export const addToCompare = async (user_id, article_id) =>
  (await api.post("/compare/add", { user_id, article_id })).data;

export const getCompareList = async (user_id) =>
  (await api.get(`/compare/list/${user_id}`)).data;

export const clearCompare = async (user_id) =>
  (await api.delete(`/compare/clear/${user_id}`)).data;

// ------------------------------------------------------
// 🌍 GEO APIs
// ------------------------------------------------------
export const getNewsByGeo = async (country, state = "", city = "") =>
  (await api.get("/geo/news", { params: { country, state, city } })).data;

export const getGeoHeatmap = async () =>
  (await api.get("/geo/heatmap")).data;

export const saveGeoTag = async (article_url, country, state, city) =>
  (await api.post("/geo/tag", { article_url, country, state, city })).data;

export const getGeoAnalytics = async () =>
  (await api.get("/geo/analytics")).data;
