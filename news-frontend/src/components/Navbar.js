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
      <div className="flex items-center gap-2">
        <img src="/trendvista_logo.png" alt="TrendVista logo" className="h-8 w-8 rounded-full bg-white" />
        <span className="text-xl font-bold tracking-tight">TrendVista</span>
      </div>
      <div className="flex items-center gap-6 text-base">
        <Link to="/" className="hover:underline">Home</Link>
        
        
        {token ? (
          <>
            {/* ✅ Show these ONLY when logged in */}
            <Link to="/profile" className="hover:underline flex items-center gap-1">
              👤 Profile
            </Link>
            <button onClick={handleLogout} className="hover:underline">Logout</button>
          </>
        ) : (
          <>
            {/* ✅ Show these ONLY when NOT logged in */}
            <Link to="/login" className="hover:underline">Login</Link>
            <Link to="/register" className="hover:underline">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
