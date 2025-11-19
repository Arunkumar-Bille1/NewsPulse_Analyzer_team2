import React from "react";
import { useNavigate } from "react-router-dom";

function Settings() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token"); // check login status

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-6">
      <div className="bg-white shadow-lg rounded-2xl p-8 w-full max-w-md">

        <h1 className="text-2xl font-bold mb-6 text-center text-indigo-600">
          Settings
        </h1>

        {/* If User is Logged In */}
        {token ? (
          <div className="space-y-4">
            <button
              onClick={() => navigate("/profile")}
              className="w-full p-3 bg-indigo-600 text-white rounded-xl shadow hover:bg-indigo-700 transition"
            >
              Profile Management
            </button>
          </div>
        ) : (
          // If NOT Logged In
          <div className="text-center">
            <p className="text-gray-600 mb-4">
              You are not logged in. Please login to access settings.
            </p>

            <button
              onClick={() => navigate("/login")}
              className="px-6 py-3 bg-indigo-600 text-white rounded-xl shadow hover:bg-indigo-700 transition"
            >
              Login
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default Settings;
