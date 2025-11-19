import axios from "axios";

const API_BASE = process.env.REACT_APP_API_BASE || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
});
// AUTH HEADERS
api.interceptors.request.use((config) => {
  try {
    const token = localStorage.getItem("token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  } catch {}
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (error) => {
    const status = error?.response?.status;
    const url = error?.config?.url || "";

    if (
      status === 401 &&
      (url.startsWith("/users/me") ||
        url.startsWith("/admin") ||
        url.startsWith("/auth"))
    ) {
      localStorage.removeItem("token");
      localStorage.removeItem("user_email");
      if (window) window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ------------------------------------------------------
// ⛳ AUTH
// ------------------------------------------------------
export const registerUser = (data) => api.post("/auth/register", data);
export const loginUser = (email, password) =>
  api.post("/auth/login", { email, password });
export const getCurrentUser = async () => (await api.get("/users/me")).data;

export const forgotPassword = (email) =>
  api.post("/auth/forgot-password", { email });

export const resetPassword = (token, password) =>
  api.post("/auth/reset-password", {
    token,
    new_password: password   // MUST MATCH FastAPI
  });


// ------------------------------------------------------
// 🧩 ADMIN
// ------------------------------------------------------
export const getAdminUsers = async () => (await api.get("/admin/users")).data;
export const getAdminStats = async () =>
  (await api.get("/admin/dashboard")).data;

export const deleteAdminUser = async (id) =>
  (await api.delete(`/admin/users/${id}`)).data;

export const getSystemStatus = async () =>
  (await api.get("/admin/system_status")).data;

export const getInsights = async () => (await api.get("/admin/insights")).data;

// ------------------------------------------------------
// 📰 NEWS / TREND EXPLORER (UI-2)
// ------------------------------------------------------

// 🔍 Search news
export const searchArticles = async (query) => {
  const res = await api.get("/news", { params: { query } });
  return res.data; // { articles, processed_query }
};

// ⭐ Default trending
export const getTrendingArticles = async () => {
  const res = await api.get("/news", { params: { query: "trending" } });
  return res.data;
};

// 🎯 Category-based news (Technology, Business...)
export const getCategoryArticles = async (category) => {
  const res = await api.get("/news", { params: { query: category } });
  return res.data;
};

// 📄 Single article analysis (if backend supports)
export const getArticleDetails = async (url) => {
  const res = await api.get("/article/details", { params: { url } });
  return res.data;
};


// 🔥 Trend Detection (already existing)
export const detectTrends = async (range = "7d") => {
  return (await api.get("/detect-trends/topics", { params: { range } })).data;
};
export default api;
// ------------------------------------------------------
// ⭐ BOOKMARK API (FINAL CORRECT VERSION)
// ------------------------------------------------------

// Add bookmark
export const addBookmark = (user_id, article) =>
  api.post("/bookmarks/add", { user_id, article });

// Remove bookmark
export const removeBookmark = (user_id, article_url) =>
  api.delete("/bookmarks/remove", {
    data: { user_id, article_url }
  });

// Get all bookmarks (DO NOT ENCODE HERE)
export const getBookmarks = (user_id) =>
  api.get(`/bookmarks/${user_id}`);

// Check if already bookmarked
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
