import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";

// Public pages
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Settings from "./pages/Settings";

// Dashboard pages
import Home from "./pages/Home";
import Profile from "./pages/Profile";
import AdminDashboard from "./pages/AdminDashboard";
import ArticleDetails from "./pages/ArticleDetails";
import RawAnalysis from "./pages/RawAnalysis";
import Trending from "./pages/Trending";
import TopicTrends from "./pages/TopicTrends";
import Compare from "./pages/compare";
import SavedNews from "./pages/SavedNews";
import GeoDashboard from "./pages/GeoDashboard";
import GeoFilter from "./components/GeoFilter";

function App() {
  return (
    <Router>
      <Routes>

        {/* PUBLIC ROUTES */}
        <Route
          path="/login"
          element={
            <>
              <Navbar />
              <div className="p-6 bg-gray-50 min-h-screen mt-20">
                <Login />
              </div>
            </>
          }
        />

        <Route
          path="/register"
          element={
            <>
              <Navbar />
              <div className="p-6 bg-gray-50 min-h-screen mt-20">
                <Register />
              </div>
            </>
          }
        />

        <Route
          path="/forgot-password"
          element={
            <>
              <Navbar />
              <div className="p-6 bg-gray-50 min-h-screen mt-20">
                <ForgotPassword />
              </div>
            </>
          }
        />

        <Route
          path="/reset-password"
          element={
            <>
              <Navbar />
              <div className="p-6 bg-gray-50 min-h-screen mt-20">
                <ResetPassword />
              </div>
            </>
          }
        />


        {/* =======================
            DASHBOARD ROUTES
            (Sidebar + Navbar Layout)
        ======================== */}

        {/* HOME */}
        <Route
          path="/"
          element={
            <div className="flex">
              <Sidebar />
              <div className="flex-1 ml-64">
                <Navbar />
                <div className="p-6 bg-gray-50 min-h-screen mt-20">
                  <Home />
                </div>
              </div>
            </div>
          }
        />

        {/* PROFILE */}
        <Route
          path="/profile"
          element={
            <div className="flex">
              <Sidebar />
              <div className="flex-1 ml-64">
                <Navbar />
                <div className="p-6 bg-gray-50 min-h-screen mt-20">
                  <Profile />
                </div>
              </div>
            </div>
          }
        />

        {/* ADMIN */}
        <Route
          path="/admin"
          element={
            <div className="flex">
              <Sidebar />
              <div className="flex-1 ml-64">
                <Navbar />
                <div className="p-6 bg-gray-50 min-h-screen mt-20">
                  <AdminDashboard />
                </div>
              </div>
            </div>
          }
        />

        {/* ARTICLE DETAILS */}
        <Route
          path="/article/:id"
          element={
            <div className="flex">
              <Sidebar />
              <div className="flex-1 ml-64">
                <Navbar />
                <div className="p-6 bg-gray-50 min-h-screen mt-20">
                  <ArticleDetails />
                </div>
              </div>
            </div>
          }
        />

        {/* RAW ANALYSIS */}
        <Route
          path="/analyze"
          element={
            <div className="flex">
              <Sidebar />
              <div className="flex-1 ml-64">
                <Navbar />
                <div className="p-6 bg-gray-50 min-h-screen mt-20">
                  <RawAnalysis />
                </div>
              </div>
            </div>
          }
        />

        {/* TRENDING */}
        <Route
          path="/trending"
          element={
            <div className="flex">
              <Sidebar />
              <div className="flex-1 ml-64">
                <Navbar />
                <div className="p-6 bg-gray-50 min-h-screen mt-20">
                  <Trending />
                </div>
              </div>
            </div>
          }
        />

        {/* COMPARE PAGE */}
        <Route
          path="/compare"
          element={
            <div className="flex">
              <Sidebar />
              <div className="flex-1 ml-64">
                <Navbar />
                <div className="p-6 bg-gray-50 min-h-screen mt-20">
                  <Compare userId={JSON.parse(localStorage.getItem("user"))?.id} />
                </div>
              </div>
            </div>
          }
        />

        {/* TOPIC TRENDS */}
        <Route
          path="/topic-trends"
          element={
            <div className="flex">
              <Sidebar />
              <div className="flex-1 ml-64">
                <Navbar />
                <div className="p-6 bg-gray-50 min-h-screen mt-20">
                  <TopicTrends />
                </div>
              </div>
            </div>
          }
        />

        {/* ⭐ SAVED NEWS (BOOKMARKS) — FIX ADDED */}
        <Route
          path="/SavedNews"
          element={
            <div className="flex">
              <Sidebar />
              <div className="flex-1 ml-64">
                <Navbar />
                <div className="p-6 bg-gray-50 min-h-screen mt-20">
                  <SavedNews />
                </div>
              </div>
            </div>
          }
        />
        <Route
          path="/settings"
          element={
            <div className="flex">
              <Sidebar />
              <div className="flex-1 ml-64">
                <Navbar />
                <div className="p-6 bg-gray-50 min-h-screen mt-20">
                  <Settings />
                </div>
              </div>
            </div>
          }
        />
        {/* ⭐ GEO DASHBOARD ROUTE */}
        <Route
          path="/GeoDashboard"
          element={
            <div className="flex">
              <Sidebar />
              <div className="flex-1 ml-64">
                <Navbar />
                <div className="p-6 bg-gray-50 min-h-screen mt-20">
                  <GeoDashboard />
                </div>
              </div>
            </div>
          }
        />


      </Routes>
    </Router>
  );
}

export default App;
