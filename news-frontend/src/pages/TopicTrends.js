import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  LineChart,
  Line,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

// 🌈 COLORS for charts
const COLORS = ["#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"];

// 🎨 Reusable UI components
const Card = ({ children, className = "" }) => (
  <motion.div
    className={`bg-white/70 backdrop-blur-lg rounded-2xl shadow-xl border border-gray-200 transition-all ${className}`}
    whileHover={{ scale: 1.01 }}
  >
    {children}
  </motion.div>
);

const CardHeader = ({ children, className = "" }) => (
  <div className={`border-b border-gray-200 p-4 ${className}`}>{children}</div>
);

const CardTitle = ({ children, className = "" }) => (
  <h2 className={`text-lg font-semibold text-gray-800 ${className}`}>{children}</h2>
);

const CardContent = ({ children, className = "" }) => (
  <div className={`p-4 ${className}`}>{children}</div>
);

const Button = ({ children, onClick, active = false }) => (
  <motion.button
    onClick={onClick}
    whileTap={{ scale: 0.95 }}
    className={`px-5 py-2 rounded-lg text-sm font-semibold shadow transition-all duration-300 ${
      active
        ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md"
        : "border border-gray-300 text-gray-700 bg-white hover:bg-gray-100"
    }`}
  >
    {children}
  </motion.button>
);

// 🌟 Main Component
const TopicTrends = () => {
  const [timeRange, setTimeRange] = useState("7d");
  const [trendData, setTrendData] = useState(null);
  const [loading, setLoading] = useState(true);

  // ✅ Fetch from backend
  const fetchTrendData = async (range) => {
    setLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/detect-trends/topics?range=${range}`);
      const data = await res.json();
      setTrendData(data);
    } catch (err) {
      console.error("Error fetching trend data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrendData(timeRange);
  }, [timeRange]);

  // Default mock data
  const sentimentData = trendData?.sentiment_distribution || [
    { name: "Positive", value: 45 },
    { name: "Neutral", value: 35 },
    { name: "Negative", value: 20 },
  ];

  const topTopics = trendData?.top_topics || [
    { topic: "AI", count: 210 },
    { topic: "Blockchain", count: 180 },
    { topic: "Healthcare", count: 160 },
    { topic: "Climate", count: 130 },
    { topic: "Economy", count: 100 },
  ];

  const timeSeriesData =
    trendData?.sentiment_over_time ||
    Array.from({ length: 7 }, (_, i) => ({
      date: `Day ${i + 1}`,
      positive: 40 + Math.random() * 10,
      neutral: 35 + Math.random() * 10,
      negative: 25 + Math.random() * 10,
    }));

  // ✨ Background animation
  const bgGradient =
    timeRange === "7d"
      ? "from-blue-100 via-indigo-50 to-white"
      : timeRange === "30d"
      ? "from-green-100 via-emerald-50 to-white"
      : "from-purple-100 via-pink-50 to-white";

  return (
    <motion.div
      className={`min-h-screen bg-gradient-to-br ${bgGradient} p-6`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      <motion.div
        className="max-w-6xl mx-auto space-y-8"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header */}
        <Card className="overflow-hidden">
          <CardHeader className="bg-gradient-to-r from-slate-900 via-blue-800 to-indigo-700 text-white rounded-t-2xl shadow">
            <motion.h1
              className="text-3xl font-bold text-center tracking-wide"
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5 }}
            >
              TrendPulse AI – Topic Trends & Sentiment Insights
            </motion.h1>
          </CardHeader>

          <CardContent>
            {/* Range Buttons */}
            <motion.div
              className="flex justify-center gap-4 mb-8"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              {[
                { label: "Last 7 Days", value: "7d" },
                { label: "Last 30 Days", value: "30d" },
                { label: "Last 90 Days", value: "90d" },
              ].map((opt) => (
                <Button
                  key={opt.value}
                  onClick={() => setTimeRange(opt.value)}
                  active={timeRange === opt.value}
                >
                  {opt.label}
                </Button>
              ))}
            </motion.div>

            {/* Loader */}
            {loading ? (
              <motion.p
                className="text-center text-gray-600 text-lg mt-6"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                ⏳ Fetching insights for <strong>{timeRange}</strong>...
              </motion.p>
            ) : (
              <>
                {/* Top Topics & Sentiment Pie */}
                <div className="grid md:grid-cols-2 gap-8">
                  {/* Bar Chart */}
                  <motion.div
                    initial={{ y: 40, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.6 }}
                  >
                    <Card>
                      <CardHeader>
                        <CardTitle>🔥 Top Trending Topics  </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ResponsiveContainer width="100%" height={260}>
                          <BarChart data={topTopics}>
                            <XAxis dataKey="topic" />
                            <YAxis />
                            <Tooltip />
                            <Bar
                              dataKey="count"
                              radius={[8, 8, 0, 0]}
                              fill="url(#barGradient)"
                            />
                            <defs>
                              <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.9} />
                                <stop offset="95%" stopColor="#60a5fa" stopOpacity={0.6} />
                              </linearGradient>
                            </defs>
                          </BarChart>
                        </ResponsiveContainer>
                      </CardContent>
                    </Card>
                  </motion.div>

                  {/* Pie Chart */}
                  <motion.div
                    initial={{ y: 40, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                  >
                    <Card>
                      <CardHeader>
                        <CardTitle>💬 Sentiment Distribution</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ResponsiveContainer width="100%" height={260}>
                          <PieChart>
                            <Pie
                              data={sentimentData}
                              cx="50%"
                              cy="50%"
                              outerRadius={90}
                              label
                              dataKey="value"
                            >
                              {sentimentData.map((entry, index) => (
                                <Cell key={index} fill={COLORS[index % COLORS.length]} />
                              ))}
                            </Pie>
                            <Tooltip />
                            <Legend />
                          </PieChart>
                        </ResponsiveContainer>
                      </CardContent>
                    </Card>
                  </motion.div>
                </div>

                {/* Line Chart */}
                <motion.div
                  initial={{ y: 40, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                >
                  <Card className="mt-10">
                    <CardHeader>
                      <CardTitle>📈 Sentiment Trend Over Time</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={320}>
                        <LineChart data={timeSeriesData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          <Line
                            type="monotone"
                            dataKey="positive"
                            stroke="#22c55e"
                            strokeWidth={2}
                            dot={false}
                          />
                          <Line
                            type="monotone"
                            dataKey="neutral"
                            stroke="#facc15"
                            strokeWidth={2}
                            dot={false}
                          />
                          <Line
                            type="monotone"
                            dataKey="negative"
                            stroke="#ef4444"
                            strokeWidth={2}
                            dot={false}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </motion.div>

                {/* Animated Feature Tags */}
                <motion.div
                  className="flex flex-wrap justify-center gap-3 mt-8"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.6 }}
                >
                  {[
                    "AI-Powered Insights",
                    "Dynamic Time Ranges",
                    "Smooth Animations",
                    "Interactive Dashboards",
                    "Real-time Analysis",
                  ].map((feature, i) => (
                    <motion.span
                      key={i}
                      whileHover={{ scale: 1.1 }}
                      className="px-4 py-1.5 bg-blue-50 text-blue-800 rounded-full text-sm font-medium shadow-sm border border-blue-100"
                    >
                      {feature}
                    </motion.span>
                  ))}
                </motion.div>
              </>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
};

export default TopicTrends;
