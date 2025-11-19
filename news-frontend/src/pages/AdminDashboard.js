// src/pages/AdminDashboard.js
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  getCurrentUser,
  getAdminUsers,
  getAdminStats,
  getSystemStatus,
  getInsights,
} from '../api';
import api from '../api';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [meUser, setMeUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const run = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      try {
        const me = await getCurrentUser();
        setMeUser(me);
        if ((me?.role || '').toLowerCase() !== 'admin') {
          setMessage('ERROR: Access denied. Admin privileges required.');
          setTimeout(() => navigate('/'), 2000);
          return;
        }

        const [usersRes, statsRes, sysRes, insRes] = await Promise.all([
          getAdminUsers(),
          getAdminStats(),
          getSystemStatus(),
          getInsights(),
        ]);

        const list = Array.isArray(usersRes)
          ? usersRes
          : usersRes?.data || [];
        setUsers(list);

        const s = statsRes?.data || statsRes || null;
        if (s) {
          setStats({
            total_users: s.total_users ?? s.total ?? 0,
            admin_users: s.admin_users ?? s.admins ?? 0,
            regular_users:
              (s.total_users ?? s.total ?? 0) -
              (s.admin_users ?? s.admins ?? 0),
          });
        } else {
          const total = list.length;
          const admins = list.filter(
            (x) => (x.role || '').toLowerCase() === 'admin'
          ).length;
          setStats({
            total_users: total,
            admin_users: admins,
            regular_users: total - admins,
          });
        }

        setSystemStatus(sysRes?.data || sysRes);
        setInsights(insRes?.data || insRes);
      } catch (err) {
        console.error('Admin load failed:', err);
        setMessage('ERROR: Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };
    run();
  }, [navigate]);

  const handleDeleteUser = async (userId) => {
    if (
      !window.confirm(
        'Are you sure you want to delete this user? This action cannot be undone.'
      )
    )
      return;
    try {
      await api.delete(`/admin/users/${userId}`);
      setMessage('SUCCESS: User deleted successfully');
      setTimeout(() => setMessage(''), 3000);
      const refreshed = await getAdminUsers();
      const list = Array.isArray(refreshed)
        ? refreshed
        : refreshed?.data || [];
      setUsers(list);
      const total = list.length;
      const admins = list.filter(
        (x) => (x.role || '').toLowerCase() === 'admin'
      ).length;
      setStats({
        total_users: total,
        admin_users: admins,
        regular_users: total - admins,
      });
    } catch (error) {
      console.error('Error deleting user:', error);
      setMessage('ERROR: Failed to delete user');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-gray-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Admin Dashboard
              </h1>
              <p className="text-gray-600 mt-1">
                Manage users and monitor system activity
              </p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => navigate('/profile')}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-semibold border border-gray-300 transition"
              >
                My Profile
              </button>
              <button
                onClick={() => navigate('/')}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold transition"
              >
                Back to Home
              </button>
            </div>
          </div>
        </div>

        {/* Message alert */}
        {message && (
          <div
            className={`mb-6 p-4 rounded-lg border ${
              message.startsWith('SUCCESS')
                ? 'bg-green-50 text-green-800 border-green-300'
                : 'bg-red-50 text-red-800 border-red-300'
            }`}
          >
            <div className="flex items-center">
              {message.startsWith('SUCCESS') ? (
                <svg
                  className="w-5 h-5 mr-2 text-green-600"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
              ) : (
                <svg
                  className="w-5 h-5 mr-2 text-red-600"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
              {message.replace('SUCCESS: ', '').replace('ERROR: ', '')}
            </div>
          </div>
        )}

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            {[
              {
                title: 'Total Users',
                value: stats.total_users,
                subtitle: 'Registered accounts',
                color: 'indigo',
              },
              {
                title: 'Admin Users',
                value: stats.admin_users,
                subtitle: 'Administrator accounts',
                color: 'purple',
              },
              {
                title: 'Regular Users',
                value: stats.regular_users,
                subtitle: 'Standard accounts',
                color: 'green',
              },
              {
                title: 'System Status',
                value: (
                  <span className="text-green-600 font-semibold">Online</span>
                ),
                subtitle: 'All services operational',
                color: 'blue',
              },
            ].map((card, i) => (
              <div
                key={i}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 font-semibold mb-1">
                      {card.title}
                    </p>
                    <p className="text-3xl font-bold text-gray-900">
                      {card.value}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {card.subtitle}
                    </p>
                  </div>
                  <div
                    className={`w-12 h-12 bg-${card.color}-100 rounded-lg flex items-center justify-center`}
                  >
                    <svg
                      className={`w-6 h-6 text-${card.color}-600`}
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" />
                    </svg>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Advanced Insights + System Metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Insights Chart */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Advanced Insights Dashboard
            </h2>
            {insights ? (
              <>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={insights.chart_series}>
                      <XAxis dataKey="day" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="Technology"
                        stroke="#00b894"
                      />
                      <Line
                        type="monotone"
                        dataKey="Environment"
                        stroke="#0984e3"
                      />
                      <Line
                        type="monotone"
                        dataKey="Economy"
                        stroke="#fdcb6e"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-4 bg-green-50 border border-green-200 rounded-lg p-3">
                  <p className="text-green-700 font-semibold">
                    Trend Spike Detected
                  </p>
                  <p className="text-sm text-green-600">
                    {insights.trend_spike}
                  </p>
                </div>
                <div className="flex flex-wrap gap-4 mt-4">
                  {Object.entries(insights.correlations || {}).map(([k, v]) => (
                    <div
                      key={k}
                      className="flex-1 bg-gray-50 border border-gray-200 rounded-lg p-4 text-center shadow-sm"
                    >
                      <p className="text-gray-600 text-sm">{k}</p>
                      <p className="text-2xl font-bold text-gray-900">{v}</p>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <p className="text-gray-600">Loading insights...</p>
            )}
          </div>

          {/* System Status */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              System Health Overview
            </h2>
            {systemStatus ? (
              <div className="space-y-3">
                <div className="flex justify-between text-sm font-semibold">
                  <span>System Uptime</span>
                  <span>{systemStatus.system_uptime}</span>
                </div>
                <div className="flex justify-between text-sm font-semibold">
                  <span>Avg. Response Time</span>
                  <span>{systemStatus.avg_response_time}</span>
                </div>
                <div className="flex justify-between text-sm font-semibold">
                  <span>Daily Requests</span>
                  <span>{systemStatus.daily_requests}</span>
                </div>
                <div className="flex justify-between text-sm font-semibold">
                  <span>Status</span>
                  <span className="text-green-600">{systemStatus.status}</span>
                </div>
                <div className="mt-4 text-xs text-gray-500">
                  Last checked:{' '}
                  {new Date(systemStatus.last_checked).toLocaleString()}
                </div>
              </div>
            ) : (
              <p className="text-gray-600">Loading system data...</p>
            )}
          </div>
        </div>

        {/* Users Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-900">All Users</h2>
                <p className="text-gray-600 text-sm mt-1">
                  Manage and monitor user accounts ({users.length} total)
                </p>
              </div>
            </div>
          </div>

          {users.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    {['Name', 'Email', 'Role', 'Country', 'Actions'].map(
                      (th) => (
                        <th
                          key={th}
                          className="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider"
                        >
                          {th}
                        </th>
                      )
                    )}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50 transition">
                      <td className="px-6 py-4 whitespace-nowrap flex items-center">
                        <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center mr-3">
                          <span className="text-indigo-600 font-semibold text-sm">
                            {(user.name || '').charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <span className="text-sm font-semibold text-gray-900">
                          {user.name || '(no name)'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {user.email}
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            (user.role || '') === 'admin'
                              ? 'bg-indigo-100 text-indigo-700 border border-indigo-200'
                              : 'bg-gray-100 text-gray-700 border border-gray-200'
                          }`}
                        >
                          {user.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {user.country || 'Not specified'}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <button
                          onClick={() => handleDeleteUser(user.id)}
                          disabled={meUser && user.id === meUser.id}
                          className={`font-semibold ${
                            meUser && user.id === meUser.id
                              ? 'text-gray-400 cursor-not-allowed'
                              : 'text-red-600 hover:text-red-800'
                          }`}
                          title={
                            meUser && user.id === meUser.id
                              ? 'Cannot delete yourself'
                              : 'Delete user'
                          }
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center">
              <p className="text-gray-600 font-medium">No users found</p>
              <p className="text-gray-500 text-sm mt-1">
                Users will appear here once they register
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;
