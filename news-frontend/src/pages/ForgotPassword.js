import React, { useState } from "react";
import { forgotPassword } from "../api";

function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    if (!email) {
      setMessage("ERROR: Please enter your email");
      setLoading(false);
      return;
    }

    try {
      await forgotPassword(email);
      setMessage("SUCCESS: Password reset link sent! Check your email.");
      setEmailSent(true);
    } catch (error) {
      console.error("Forgot password error:", error);
      setMessage("SUCCESS: If your email exists, a reset link has been sent.");
      setEmailSent(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Left Side - Professional Clean Panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-indigo-600 p-12 flex-col justify-center">
        <div className="max-w-md">
          <h1 className="text-4xl font-bold text-white mb-6">
            Password Recovery
          </h1>
          <p className="text-lg text-indigo-100 mb-8 leading-relaxed">
            We will send you a secure link to reset your password. The link will expire after 1 hour for your security.
          </p>
          
          <div className="space-y-6">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-400 flex items-center justify-center mt-1">
                <span className="text-white text-sm font-bold">1</span>
              </div>
              <div>
                <h3 className="text-white font-semibold mb-1">Enter your email</h3>
                <p className="text-indigo-200 text-sm">Provide the email address associated with your account</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-400 flex items-center justify-center mt-1">
                <span className="text-white text-sm font-bold">2</span>
              </div>
              <div>
                <h3 className="text-white font-semibold mb-1">Check your inbox</h3>
                <p className="text-indigo-200 text-sm">We'll send you a password reset link</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-400 flex items-center justify-center mt-1">
                <span className="text-white text-sm font-bold">3</span>
              </div>
              <div>
                <h3 className="text-white font-semibold mb-1">Reset your password</h3>
                <p className="text-indigo-200 text-sm">Click the link and create a new secure password</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - KEEPING YOUR ORIGINAL GOOD DESIGN */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="bg-white border-2 border-indigo-300 rounded-2xl shadow-2xl w-full max-w-md p-8 transform hover:scale-[1.01] transition-transform duration-200">
          <div className="text-center mb-6">
            <h2 className="text-3xl font-bold text-indigo-600 mb-2">
              Forgot Password?
            </h2>
            <p className="text-gray-600 text-sm">
              Enter your email to receive a password reset link
            </p>
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

          {!emailSent ? (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block mb-2 text-sm text-gray-700 font-semibold">
                  Email Address
                </label>
                <input
                  type="email"
                  placeholder="Enter your registered email"
                  className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm transition-all"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={loading}
                />
              </div>

              <button
                type="submit"
                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg py-3 text-sm font-bold hover:from-indigo-700 hover:to-purple-700 transition-all transform hover:scale-[1.02] disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none shadow-lg"
                disabled={loading}
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Sending...
                  </span>
                ) : "Send Reset Link"}
              </button>
            </form>
          ) : (
            <div className="text-center space-y-4">
              <div className="text-6xl mb-4">
                <svg className="w-20 h-20 mx-auto text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-800">Check Your Email!</h3>
              <p className="text-gray-600 text-sm">
                We've sent a password reset link to <span className="font-semibold text-indigo-600">{email}</span>
              </p>
              <p className="text-gray-500 text-xs mt-2">
                Click the link in the email to reset your password.
              </p>
              <button
                onClick={() => {
                  setEmailSent(false);
                  setEmail("");
                  setMessage("");
                }}
                className="text-sm text-indigo-600 hover:text-indigo-800 hover:underline mt-4"
              >
                Didn't receive? Try again
              </button>
            </div>
          )}

          <div className="text-center mt-6 pt-6 border-t border-gray-200">
            <p className="text-gray-600 text-sm">
              Remember your password?{" "}
              <a href="/login" className="text-indigo-600 font-semibold hover:text-indigo-800 hover:underline transition-colors">
                Back to Login
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ForgotPassword;
