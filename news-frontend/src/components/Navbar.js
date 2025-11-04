import React from "react";
import { Link, useNavigate } from "react-router-dom";

function Navbar() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <nav className="bg-indigo-600 text-white px-4 py-3 shadow flex items-center justify-between">
      {/* Logo & Title */}
      <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate("/")}>
        <img
          src="/trendvista_logo.png"
          alt="TrendVista logo"
          className="h-8 w-8 rounded-full bg-white"
        />
        <span className="text-xl font-bold tracking-tight">TrendVista</span>
      </div>

      {/* Navigation Links */}
      <div className="flex items-center gap-6 text-base">
        <Link to="/" className="hover:underline">
          Home
        </Link>

        <Link to="/analyze" className="hover:underline px-4 py-2">
          Raw Analysis
        </Link>

        {/* ✅ Add new links for Trending and Topic Trends */}
        <Link to="/trending" className="hover:underline px-4 py-2">
          Trending
        </Link>

        <Link to="/topic-trends" className="hover:underline px-4 py-2">
          Topic Trends
        </Link>

        {/* Auth-based display */}
        {token ? (
          <>
            <Link to="/profile" className="hover:underline flex items-center gap-1">
              👤 Profile
            </Link>
            <button onClick={handleLogout} className="hover:underline">
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="hover:underline">
              Login
            </Link>
            <Link to="/register" className="hover:underline">
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
