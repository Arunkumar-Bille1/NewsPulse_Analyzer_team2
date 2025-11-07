import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

const interestOptions = [
  "Technology","Business","Politics","Sports",
  "Health","Science","Entertainment","Environment","Economy","Education"
];

function Profile() {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [activeTab, setActiveTab] = useState("account");

  // Form fields
  const [bio, setBio] = useState("");
  const [website, setWebsite] = useState("");
  const [location, setLocation] = useState("");
  const [country, setCountry] = useState("");   // NEW
  const [phone, setPhone] = useState("");
  const [preferredLanguage, setPreferredLanguage] = useState("en");
  const [interests, setInterests] = useState([]);
  const [emailNotifications, setEmailNotifications] = useState(false);
  const [trendingAlerts, setTrendingAlerts] = useState(false);

  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  // 1) Define fetchAllData first, fully closed, and with deps
  const fetchAllData = useCallback(async () => {
    try {
      const userResponse = await api.get("/users/me");
      setUser(userResponse.data);

      try {
        const profileResponse = await api.get("/profile");
        const profileData = profileResponse.data;
        setProfile(profileData);
        setBio(profileData.bio || "");
        setWebsite(profileData.website || "");
        setLocation(profileData.location || "");
        setCountry(profileData.country || ""); // NEW
        setPhone(profileData.phone || "");
        setPreferredLanguage(profileData.preferred_language || "en");
        setInterests(Array.isArray(profileData.interests) ? profileData.interests : []);
        setEmailNotifications(profileData.email_notifications || false);
        setTrendingAlerts(profileData.trending_alerts || false);
      } catch (error) {
        if (error.response?.status !== 404) console.error("Error fetching profile:", error);
      }
    } catch (error) {
      console.error("Error fetching data:", error);
      if (error.response?.status === 401) {
        localStorage.removeItem("token");
        navigate("/login");
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  // 2) Then use it in useEffect with proper deps
  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }
    fetchAllData();
  }, [token, navigate, fetchAllData]);

  // 3) Save handler (unchanged except for debug log)
  const handleSaveProfile = async (e) => {
  e.preventDefault();
  setSaving(true);
  setMessage("");

  try {
    const profileData = {
      bio, website, location, country, phone,
      preferred_language: preferredLanguage,
      interests: Array.isArray(interests) ? interests : [],
      email_notifications: emailNotifications,
      trending_alerts: trendingAlerts
    };

    if (profile) {
      console.log("sending PUT /profile", profileData); // add this
      await api.put("/profile", profileData);
      setMessage("SUCCESS: Profile updated successfully!");
    } else {
      console.log("sending POST /profile", profileData); // add this
      await api.post("/profile", profileData);
      setMessage("SUCCESS: Profile created successfully!");
    }

    setEditing(false);
    setTimeout(() => setMessage(""), 3000);
    fetchAllData();
  } catch (error) {
    console.error("Error saving profile:", error);
    setMessage("ERROR: Failed to save profile. Please try again.");
  } finally {
    setSaving(false);
  }
};



  const toggleInterest = (topic) => {
    setInterests(prev =>
      prev.includes(topic) ? prev.filter(i => i !== topic) : [...prev, topic]
    );
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-3 border-gray-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-5xl mx-auto px-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Profile Management</h1>
              <p className="text-gray-600 mt-1">Manage your account, profile, and preferences</p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => navigate("/")}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-semibold transition-colors border border-gray-300"
              >
                Back to Home
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>

        {message && (
          <div className={`mb-6 p-4 rounded-lg border ${
            message.startsWith("SUCCESS")
              ? "bg-green-50 text-green-800 border-green-300"
              : "bg-red-50 text-red-800 border-red-300"
          }`}>
            {message.replace("SUCCESS: ", "").replace("ERROR: ", "")}
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab("account")}
              className={`flex-1 px-6 py-4 font-semibold transition-colors ${
                activeTab === "account"
                  ? "text-indigo-600 border-b-2 border-indigo-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Account Info
            </button>
            <button
              onClick={() => setActiveTab("profile")}
              className={`flex-1 px-6 py-4 font-semibold transition-colors ${
                activeTab === "profile"
                  ? "text-indigo-600 border-b-2 border-indigo-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Profile Details
            </button>
            <button
              onClick={() => setActiveTab("preferences")}
              className={`flex-1 px-6 py-4 font-semibold transition-colors ${
                activeTab === "preferences"
                  ? "text-indigo-600 border-b-2 border-indigo-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Preferences
            </button>
          </div>

          <div className="p-6">
            {/* Account Info Tab */}
            {activeTab === "account" && (
              <div className="space-y-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Account Information</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="text-sm font-semibold text-gray-700">Name</label>
                    <p className="text-gray-900 mt-1 text-lg">{user?.name || "N/A"}</p>
                  </div>
                  <div>
                    <label className="text-sm font-semibold text-gray-700">Email</label>
                    <p className="text-gray-900 mt-1 text-lg">{user?.email || "N/A"}</p>
                  </div>
                  <div>
                    <label className="text-sm font-semibold text-gray-700">Country</label>
                    <p className="text-gray-900 mt-1 text-lg">{user?.country || "Not specified"}</p>
                  </div>
                  <div>
                    <label className="text-sm font-semibold text-gray-700">Role</label>
                    <p className="mt-1">
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        user?.role === "admin"
                          ? "bg-indigo-100 text-indigo-700"
                          : "bg-gray-100 text-gray-700"
                      }`}>
                        {user?.role || "user"}
                      </span>
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Profile Details Tab */}
            {activeTab === "profile" && (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold text-gray-900">Profile Details</h2>
                  {!editing && (
                    <button
                      onClick={() => setEditing(true)}
                      className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold transition-colors"
                    >
                      Edit Profile
                    </button>
                  )}
                </div>

                {editing ? (
                  <form onSubmit={handleSaveProfile} className="space-y-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-1">Bio</label>
                      <textarea
                        value={bio}
                        onChange={(e) => setBio(e.target.value)}
                        placeholder="Tell us about yourself..."
                        rows={4}
                        className="w-full border-2 border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Website</label>
                        <input
                          type="url"
                          value={website}
                          onChange={(e) => setWebsite(e.target.value)}
                          placeholder="https://yourwebsite.com"
                          className="w-full border-2 border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Location</label>
                        <input
                          type="text"
                          value={location}
                          onChange={(e) => setLocation(e.target.value)}
                          placeholder="City"
                          className="w-full border-2 border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Country</label>
                        <input
                          type="text"
                          value={country}
                          onChange={(e) => setCountry(e.target.value)}
                          placeholder="Country"
                          className="w-full border-2 border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Phone</label>
                        <input
                          type="tel"
                          value={phone}
                          onChange={(e) => setPhone(e.target.value)}
                          placeholder="+1 234 567 8900"
                          className="w-full border-2 border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        />
                      </div>
                    </div>

                    <div className="flex space-x-3">
                      <button
                        type="submit"
                        disabled={saving}
                        className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 text-white rounded-lg font-semibold transition-colors"
                      >
                        {saving ? "Saving..." : "Save Changes"}
                      </button>
                      <button
                        type="button"
                        onClick={() => setEditing(false)}
                        className="px-6 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg font-semibold transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-semibold text-gray-700">Bio</label>
                      <p className="text-gray-900 mt-1">{bio || "No bio added yet"}</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-semibold text-gray-700">Website</label>
                        <p className="text-gray-900 mt-1">
                          {website ? (
                            <a href={website} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">
                              {website}
                            </a>
                          ) : "No website added"}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm font-semibold text-gray-700">Location</label>
                        <p className="text-gray-900 mt-1">{location || "No location added"}</p>
                      </div>
                    </div>

                    <div>
                      <label className="text-sm font-semibold text-gray-700">Phone</label>
                      <p className="text-gray-900 mt-1">{phone || user?.phone_number || "No phone added"}</p>
                    </div>

                    <div>
                      <label className="text-sm font-semibold text-gray-700">Interests</label>
                      <p className="text-gray-900 mt-1">
                        {Array.isArray(interests) && interests.length > 0 ? interests.join(", ") : "No interests selected"}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Preferences Tab */}
            {activeTab === "preferences" && (
              <form onSubmit={handleSaveProfile} className="space-y-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">User Preferences</h2>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Preferred Language</label>
                  <div className="flex space-x-3">
                    <button
                      type="button"
                      onClick={() => setPreferredLanguage("en")}
                      className={`px-5 py-2 rounded-lg border transition ${
                        preferredLanguage === "en"
                          ? "bg-indigo-100 border-indigo-500 text-indigo-700 font-semibold"
                          : "bg-white border-gray-300 text-gray-700 hover:bg-gray-50"
                      }`}
                    >
                      English
                    </button>
                    <button
                      type="button"
                      onClick={() => setPreferredLanguage("hi")}
                      className={`px-5 py-2 rounded-lg border transition ${
                        preferredLanguage === "hi"
                          ? "bg-indigo-100 border-indigo-500 text-indigo-700 font-semibold"
                          : "bg-white border-gray-300 text-gray-700 hover:bg-gray-50"
                      }`}
                    >
                      Hindi
                    </button>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Areas of Interest</label>
                  <div className="flex flex-wrap gap-2">
                    {interestOptions.map(topic => (
                      <button
                        key={topic}
                        type="button"
                        onClick={() => toggleInterest(topic)}
                        className={`px-4 py-2 rounded-full border text-sm transition ${
                          interests.includes(topic)
                            ? "border-indigo-500 bg-indigo-100 text-indigo-700 font-semibold"
                            : "border-gray-300 bg-gray-50 text-gray-700 hover:bg-gray-100"
                        }`}
                      >
                        {topic}
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Notifications</label>
                  <div className="space-y-3">
                    <label className="flex items-center gap-3 bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 cursor-pointer hover:bg-gray-100 transition">
                      <input
                        type="checkbox"
                        checked={emailNotifications}
                        onChange={(e) => setEmailNotifications(e.target.checked)}
                        className="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
                      />
                      <span className="text-gray-700">Email Notifications</span>
                    </label>
                    <label className="flex items-center gap-3 bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 cursor-pointer hover:bg-gray-100 transition">
                      <input
                        type="checkbox"
                        checked={trendingAlerts}
                        onChange={(e) => setTrendingAlerts(e.target.checked)}
                        className="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
                      />
                      <span className="text-gray-700">Trending Alerts</span>
                    </label>
                  </div>
                </div>
                <div className="flex space-x-3 pt-4">
                  <button
                    type="submit"
                    disabled={saving}
                    className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 text-white rounded-lg font-semibold transition-colors"
                  >
                    {saving ? "Saving..." : "Save Preferences"}
                  </button>
                  <button
                    type="button"
                    onClick={() => navigate("/")}
                    className="px-6 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg font-semibold transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>

        {user?.role === "admin" && (
          <div className="bg-indigo-50 border-2 border-indigo-200 rounded-lg p-6">
            <h3 className="text-lg font-bold text-indigo-900 mb-2">Admin Access</h3>
            <p className="text-indigo-700 mb-4">You have administrator privileges</p>
            <button
              onClick={() => navigate("/admin")}
              className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold transition-colors"
            >
              Go to Admin Dashboard
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default Profile;
