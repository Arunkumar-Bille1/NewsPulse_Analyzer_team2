import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../api";

function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [country, setCountry] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const getPasswordStrength = (pwd) => {
    if (!pwd) return { strength: 0, text: "", color: "" };
    let strength = 0;
    if (pwd.length >= 8) strength += 25;
    if (pwd.length >= 12) strength += 25;
    if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) strength += 25;
    if (/\d/.test(pwd)) strength += 15;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(pwd)) strength += 10;

    if (strength < 40) return { strength, text: "Weak", color: "text-red-600" };
    if (strength < 70) return { strength, text: "Medium", color: "text-yellow-600" };
    return { strength, text: "Strong", color: "text-green-600" };
  };

  const passwordStrength = getPasswordStrength(password);


// Replace your current submit handler
const handleRegister = async (e) => {
  e.preventDefault();
  setMessage('');
  setLoading(true);

  try {
    if (!name?.trim() || !email?.trim() || !password?.trim()) {
      setMessage('ERROR: Name, email and password are required.');
      return;
    }
    if (password !== confirm) {
      setMessage('ERROR: Passwords do not match.');
      return;
    }
    // Validate phone number (optional but must be exactly 10 digits)
    if (phoneNumber && !/^\d{10}$/.test(phoneNumber)) {
      setMessage("ERROR: Phone number must be exactly 10 digits.");
      setLoading(false);
      return;
    }

    const payload = {
      name: name.trim(),
      email: email.trim(),
      password,
      ...(phoneNumber ? { phonenumber: phoneNumber } : {}),
      ...(country ? { country } : {}),
    };

    const res = await registerUser(payload);

    const token =
      res?.data?.access_token ||
      res?.data?.accesstoken ||
      res?.data?.token ||
      null;

    if (token) {
      localStorage.setItem('token', token);
      localStorage.setItem('user_email', payload.email);
      setMessage('SUCCESS: Account created! Redirecting...');
      setTimeout(() => navigate('/'), 800);
    } else {
      setMessage('SUCCESS: Account created! Please log in.');
      setTimeout(() => navigate('/login'), 800);
    }
  } catch (error) {
    console.error('Registration error:', error?.response?.data || error.message);
    const status = error?.response?.status;
    const detail =
      error?.response?.data?.detail ||
      error?.response?.data?.message ||
      error?.message;

    if (status === 400 && /already/i.test(String(detail))) {
      setMessage('ERROR: Email already registered.');
    } else if (status === 422) {
      setMessage('ERROR: Invalid form data. Please check inputs.');
    } else {
      setMessage(`ERROR: Registration failed. ${detail || 'Please try again.'}`);
    }
  } finally {
    setLoading(false);
  }
};


  return (
    <div className="min-h-screen flex bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Left Side - Clean Professional Panel (NO FAKE STATS) */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-indigo-600 to-purple-700 p-12 flex-col justify-center relative overflow-hidden">
        {/* Subtle decorative circles */}
        <div className="absolute top-20 right-20 w-64 h-64 bg-white opacity-5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 left-20 w-48 h-48 bg-white opacity-5 rounded-full blur-3xl"></div>

        <div className="relative z-10 max-w-md mx-auto">
          <h1 className="text-4xl font-bold text-white mb-4 leading-tight">
            Join TrendVista Today
          </h1>
          <p className="text-lg text-indigo-100 mb-10 leading-relaxed">
            Create your account and unlock personalized news intelligence powered by advanced AI technology.
          </p>

          <div className="space-y-4">
            <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-5 border border-white border-opacity-20 hover:bg-opacity-15 transition-all">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 mt-1">
                  <div className="w-10 h-10 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                    </svg>
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-white font-semibold mb-1 text-lg">Free Forever</h3>
                  <p className="text-indigo-100 text-sm">No credit card required, cancel anytime</p>
                </div>
              </div>
            </div>

            <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-5 border border-white border-opacity-20 hover:bg-opacity-15 transition-all">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 mt-1">
                  <div className="w-10 h-10 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"/>
                      <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z"/>
                    </svg>
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-white font-semibold mb-1 text-lg">AI-Powered Insights</h3>
                  <p className="text-indigo-100 text-sm">Smart analysis of global news trends</p>
                </div>
              </div>
            </div>

            <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-5 border border-white border-opacity-20 hover:bg-opacity-15 transition-all">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 mt-1">
                  <div className="w-10 h-10 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd"/>
                    </svg>
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-white font-semibold mb-1 text-lg">Personalized Experience</h3>
                  <p className="text-indigo-100 text-sm">Content curated just for you</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Registration Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 overflow-y-auto">
        <div className="bg-white border-2 border-indigo-300 rounded-2xl shadow-2xl w-full max-w-md p-8 my-8 transform hover:scale-[1.01] transition-transform duration-200">
          <div className="text-center mb-5">
            <h2 className="text-3xl font-bold text-indigo-600 mb-2">Create Account</h2>
            <p className="text-gray-600 text-sm">Join News Intelligence Platform</p>
          </div>

          {message && (
            <div className={`text-center text-sm py-3 px-4 rounded-lg border mb-5 ${
              message.startsWith("SUCCESS")
                ? "bg-green-50 text-green-800 border-green-300"
                : "bg-red-50 text-red-800 border-red-300"
            }`}>
              {message.replace("SUCCESS: ", "").replace("ERROR: ", "")}
            </div>
          )}

          <form onSubmit={handleRegister} className="space-y-3.5">
            <div>
              <label className="block mb-1.5 text-sm text-gray-700 font-semibold">Full Name</label>
              <input
                type="text"
                placeholder="Enter your full name"
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm transition-all"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <div>
              <label className="block mb-1.5 text-sm text-gray-700 font-semibold">Email Address</label>
              <input
                type="email"
                placeholder="Enter your email"
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm transition-all"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <div>
              <label className="block mb-1.5 text-sm text-gray-700 font-semibold">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Min 6 characters"
                  className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 pr-10 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm transition-all"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500"
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
              {password && (
                <div className="mt-1.5">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs text-gray-600">Strength:</span>
                    <span className={`text-xs font-semibold ${passwordStrength.color}`}>
                      {passwordStrength.text}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div
                      className={`h-1.5 rounded-full transition-all duration-300 ${
                        passwordStrength.strength < 40 ? "bg-red-500" :
                        passwordStrength.strength < 70 ? "bg-yellow-500" : "bg-green-500"
                      }`}
                      style={{ width: `${passwordStrength.strength}%` }}
                    />
                  </div>
                </div>
              )}
            </div>

            <div>
              <label className="block mb-1.5 text-sm text-gray-700 font-semibold">Confirm Password</label>
              <input
                type="password"
                placeholder="Re-enter your password"
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm transition-all"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                required
                disabled={loading}
              />
              {confirm && password !== confirm && (
                <p className="text-xs text-red-600 mt-1">Passwords do not match</p>
              )}
            </div>

            <div>
              <label className="block mb-1.5 text-sm text-gray-700 font-semibold">Phone <span className="text-gray-400 text-xs">(Optional)</span></label>
              <input
                type="tel"
                placeholder="Your contact number"
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm transition-all"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                disabled={loading}
              />
            </div>

            <div>
              <label className="block mb-1.5 text-sm text-gray-700 font-semibold">Country <span className="text-gray-400 text-xs">(Optional)</span></label>
              <input
                type="text"
                placeholder="Your country"
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm transition-all"
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg py-3 text-sm font-bold hover:from-indigo-700 hover:to-purple-700 transition-all transform hover:scale-[1.02] disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none shadow-lg mt-2"
              disabled={loading}
            >
              {loading ? "Creating account..." : "Create Account"}
            </button>
          </form>

          <div className="text-center mt-5 pt-5 border-t border-gray-200">
            <p className="text-gray-600 text-sm">
              Already have an account?{" "}
              <a href="/login" className="text-indigo-600 font-semibold hover:text-indigo-800 hover:underline transition-colors">
                Sign In
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Register;
