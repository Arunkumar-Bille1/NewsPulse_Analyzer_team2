import React, { useEffect, useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";

function Trending() {
  const [trends, setTrends] = useState([]);
  const [topics, setTopics] = useState({});
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
  const fetchData = async () => {
    try {
      const trendRes = await axios.get("http://127.0.0.1:8000/detect-trends");
      const newsRes = await axios.get("http://127.0.0.1:8000/recent-articles");
      setTrends(trendRes.data.trending_keywords || []);
      setTopics(trendRes.data.topics || {});
      setArticles(newsRes.data.articles || []);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching data:", error);
      setLoading(false);
    }
  };

  fetchData(); // ✅ initial fetch when page loads

  // ✅ Auto-refresh every 5 minutes (300000 ms)
  const interval = setInterval(() => {
    fetchData();
  }, 300000);

  // ✅ Cleanup when component unmounts
  return () => clearInterval(interval);
}, []);


  if (loading)
    return <p className="text-center mt-10 text-gray-500 animate-pulse">Loading...</p>;

  return (
    <motion.div
      className="max-w-6xl mx-auto p-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      <motion.h1
        className="text-3xl font-bold text-center mb-8 text-blue-600"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        🔥 Trending News Insights 🔥
      </motion.h1>

      {/* Trending Keywords */}
      <motion.div
        className="bg-white shadow-lg rounded-xl p-6 mb-8"
        initial={{ opacity: 0, scale: 0.9 }}
        whileInView={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6 }}
      >
        <h2 className="text-xl font-semibold mb-4 border-b pb-2 text-gray-700">
          Top Trending Keywords
        </h2>
        <div className="flex flex-wrap gap-3">
          {trends.slice(0, 12).map((t, i) => (
            <motion.span
              key={i}
              whileHover={{ scale: 1.08 }}
              className="bg-blue-100 text-blue-800 font-medium rounded-full px-4 py-2 shadow-sm hover:bg-blue-200 cursor-pointer"
            >
              #{t.word}{" "}
              <span className="text-gray-500 text-sm">({t.frequency})</span>
            </motion.span>
          ))}
        </div>
      </motion.div>

      {/* Two-column Layout */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
       {/* 🧠 Detected Topics Section */}
<motion.div
  className="bg-white shadow-lg rounded-2xl p-6 col-span-1"
  initial={{ opacity: 0, x: -50 }}
  whileInView={{ opacity: 1, x: 0 }}
  transition={{ duration: 0.6 }}
  viewport={{ once: true }}
>
  <h2 className="text-xl font-semibold mb-4 border-b pb-2 text-gray-700 flex items-center gap-2">
    🧠 Detected Topics
  </h2>

  {Object.keys(topics).length > 0 ? (
    <motion.div
      className="flex flex-col space-y-4"
      variants={{
        hidden: { opacity: 0 },
        show: { opacity: 1, transition: { staggerChildren: 0.15 } },
      }}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true }}
    >
      {Object.entries(topics).map(([topic, words], i) => (
        <motion.div
          key={i}
          variants={{
            hidden: { opacity: 0, y: 20 },
            show: { opacity: 1, y: 0 },
          }}
          whileHover={{
            scale: 1.03,
            boxShadow: "0px 6px 20px rgba(37, 99, 235, 0.15)",
            backgroundColor: "#EFF6FF",
          }}
          transition={{ type: "spring", stiffness: 200, damping: 15 }}
          className={`rounded-xl border border-gray-200 p-4 shadow-sm transition-all duration-300 ${
            i % 2 === 0 ? "bg-gray-50" : "bg-white"
          }`}
        >
          {/* Topic Header */}
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-bold text-blue-700 text-base">
              Topic {i + 1}
            </h3>
            <span className="text-sm text-gray-500 font-medium">
              {words.length} keywords
            </span>
          </div>

          {/* Topic Keywords */}
          <p className="text-gray-700 text-sm leading-relaxed break-words">
            {words.join(", ")}
          </p>
        </motion.div>
            ))}
          </motion.div>
        ) : (
          <p className="text-gray-500 text-center">No topics detected yet.</p>
        )}
      </motion.div>


        {/* Articles */}
        <motion.div
          className="bg-white shadow-lg rounded-xl p-6 col-span-2"
          initial={{ opacity: 0, x: 50 }}
          whileInView={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-xl font-semibold mb-4 border-b pb-2 text-gray-700">
            📰 Trending News
          </h2>

          {articles.length > 0 ? (
            <motion.ul
              className="space-y-5"
              variants={{
                hidden: { opacity: 0 },
                show: { opacity: 1, transition: { staggerChildren: 0.1 } },
              }}
              initial="hidden"
              whileInView="show"
            >
              {articles.map((article, index) => (
                <motion.li
                  key={index}
                  variants={{
                    hidden: { opacity: 0, x: 80 },
                    show: { opacity: 1, x: 0 },
                  }}
                  whileHover={{
                    scale: 1.02,
                    boxShadow:
                      "0px 6px 20px rgba(0, 112, 243, 0.2), 0px 0px 10px rgba(0, 112, 243, 0.15)",
                    backgroundColor: "#F9FAFB",
                  }}
                  transition={{ type: "spring", stiffness: 200, damping: 15 }}
                  className="border rounded-lg p-4 flex items-start gap-4 cursor-pointer"
                  onClick={() => window.open(article.url, "_blank")} // ✅ opens article
                >
                  <img
                    src={article.image || "https://via.placeholder.com/120"}
                    alt={article.title}
                    className="w-28 h-24 object-cover rounded-md"
                  />
                  <div>
                    <h3 className="font-bold text-lg text-gray-900">{article.title}</h3>
                    <p className="text-gray-700 text-sm mt-1">
                      {article.description?.slice(0, 100)}...
                    </p>
                    <p className="text-gray-500 text-xs mt-2">
                      🕒 {new Date(article.published_at).toLocaleString()}
                    </p>
                  </div>
                </motion.li>
              ))}
            </motion.ul>
          ) : (
            <p className="text-gray-500">No recent articles available.</p>
          )}
        </motion.div>
      </div>
    </motion.div>
  );
}

export default Trending;