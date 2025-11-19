import React from "react";
import { useNavigate, NavLink } from "react-router-dom";
import { Bookmark, User } from "lucide-react"; 
function Navbar() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <nav
      className="
        w-full bg-white border-b shadow-sm
        fixed top-0 left-0 right-0 z-50
        flex items-center justify-between
        px-6 py-4
      "
    >
      {/* LEFT — Logo */}
      <div
        className="flex items-center gap-3 cursor-pointer"
        onClick={() => navigate("/")}
      >
        <img
          src="/trendvista_logo.png"
          alt="TrendVista logo"
          className="h-[45px] w-[45px] rounded-full" 
        />
        <span className="text-[30px] font-semibold text-indigo-600">
          TrendVista
        </span>
      </div>


      {/* RIGHT — If user NOT logged in */}
      {!token && (
        <div className="flex items-center gap-6 text-gray-700">
          <NavLink to="/login" className="text-sm font-medium hover:text-indigo-600">
            Login
          </NavLink>

          <NavLink
            to="/register"
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700"
          >
            Register
          </NavLink>
        </div>
      )}

      {/* RIGHT — If user IS logged in */}
      {token && (
        <div className="flex items-center gap-6 text-gray-700">

          {/* Saved */}
          <button
            className="text-gray-700 hover:text-indigo-600 transition cursor-pointer"
            onClick={() => navigate("/savedNews")}
          >
            <Bookmark size={26} strokeWidth={2} />
          </button>

          {/* Profile Avatar */}
          <div
          className="w-10 h-10 bg-indigo-600 rounded-full flex items-center justify-center cursor-pointer hover:bg-indigo-700 transition"
          onClick={() => navigate("/profile")}
        >
          <User size={22} className="text-white" strokeWidth={2.5} />
        </div>

          {/* Logout */}
          <button
            onClick={handleLogout}
            className="text-sm text-red-600 hover:text-red-800"
          >
            Logout
          </button>
        </div>
      )}
    </nav>
  );
}

export default Navbar;
