import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Profile from './pages/Profile';
import AdminDashboard from './pages/AdminDashboard';
import ArticleDetails from './pages/ArticleDetails';     // <-- new import for article in details
import RawAnalysis from "./pages/RawAnalysis";          // <-- new import for user raw article

function App() {
  return (
    <Router>
      <Navbar />
      <div className="p-6 bg-gray-50 min-h-screen">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/article/:id" element={<ArticleDetails />} />{/* <-- new route */}
          <Route path="/analyze" element={<RawAnalysis />} />{/* <-- new route */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
