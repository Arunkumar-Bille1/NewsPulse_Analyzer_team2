import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../api";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      const res = await loginUser(email, password);
      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("user_email", email);
      setMessage("SUCCESS: Login successful! Redirecting...");
      setTimeout(() => navigate("/"), 800);
    } catch (error) {
      console.error("Login error:", error);
      if (error.response?.status === 401) {
        setMessage("ERROR: Invalid email or password");
      } else if (error.response?.status === 404) {
        setMessage("ERROR: User not found. Please register.");
      } else {
        setMessage("ERROR: Login failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Left Side - Professional Info Panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-purple-600 p-12 flex-col justify-center">
        <div className="max-w-md">
          <h1 className="text-4xl font-bold text-white mb-6">
            Welcome Back to TrendVista
          </h1>
          <p className="text-lg text-purple-100 mb-8 leading-relaxed">
            Access your personalized news dashboard and stay updated with AI-powered global trend analysis.
          </p>
          
          <div className="space-y-6">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <svg className="w-6 h-6 text-purple-200" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"/>
                  <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z"/>
                </svg>
              </div>
              <div>
                <h3 className="text-white font-semibold mb-1">AI-Powered News Analysis</h3>
                <p className="text-purple-200 text-sm">Get intelligent insights and trend predictions</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <svg className="w-6 h-6 text-purple-200" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd"/>
                </svg>
              </div>
              <div>
                <h3 className="text-white font-semibold mb-1">Personalized Feed</h3>
                <p className="text-purple-200 text-sm">News curated based on your interests</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <svg className="w-6 h-6 text-purple-200" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
                  <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm9.707 5.707a1 1 0 00-1.414-1.414L9 12.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                </svg>
              </div>
              <div>
                <h3 className="text-white font-semibold mb-1">Save & Organize</h3>
                <p className="text-purple-200 text-sm">Bookmark articles for later reading</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="bg-white border-2 border-indigo-300 rounded-2xl shadow-2xl w-full max-w-md p-8 transform hover:scale-[1.01] transition-transform duration-200">
          <div className="text-center mb-6">
            <h2 className="text-3xl font-bold text-indigo-600 mb-2">Welcome Back</h2>
            <p className="text-gray-600 text-sm">Login to TrendVista for your personalized news feed</p>
          </div>

          {message && (
            <div className={`text-center text-sm py-3 px-4 rounded-lg border mb-6 ${
              message.startsWith("SUCCESS") 
                ? "bg-green-50 text-green-800 border-green-300" 
                : "bg-red-50 text-red-800 border-red-300"
            }`}>
              {message.replace("SUCCESS: ", "").replace("ERROR: ", "")}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label className="block mb-2 text-sm text-gray-700 font-semibold">Email Address</label>
              <input
                type="email"
                placeholder="Enter your email"
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm transition-all"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <div>
              <label className="block mb-2 text-sm text-gray-700 font-semibold">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 pr-10 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm transition-all"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showPassword ? (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg py-3 text-sm font-bold hover:from-indigo-700 hover:to-purple-700 transition-all transform hover:scale-[1.02] disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none shadow-lg"
              disabled={loading}
            >
              {loading ? "Logging in..." : "Login"}
            </button>
          </form>

          <div className="text-center mt-4">
            <a href="/forgot-password" className="text-sm text-gray-600 hover:text-indigo-600 transition-colors">
              Forgot your password?
            </a>
          </div>

          <div className="text-center mt-6 pt-6 border-t border-gray-200">
            <p className="text-gray-600 text-sm">
              Don't have an account?{" "}
              <a href="/register" className="text-indigo-600 font-semibold hover:text-indigo-800 hover:underline transition-colors">
                Create one
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
