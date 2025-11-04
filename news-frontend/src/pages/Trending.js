import React, { useEffect, useState } from "react";
import axios from "axios";

function Trending() {
  const [trends, setTrends] = useState([]);
  const [topics, setTopics] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        const res = await axios.get("http://127.0.0.1:8000/detect-trends");
        setTrends(res.data.trending_keywords || []);
        setTopics(res.data.topics || {});
        setLoading(false);
      } catch (error) {
        console.error("Error fetching trends:", error);
        setLoading(false);
      }
    };
    fetchTrends();
  }, []);

  if (loading) return <p className="text-center mt-10 text-gray-500">Loading trends...</p>;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-center mb-6 text-blue-600">🔥 Trending News Insights  🔥</h1>

      {/* Trending Keywords */}
      <div className="bg-white shadow-lg rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 border-b pb-2">Top Trending Keywords</h2>
        <ul className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {trends.map((t, index) => (
            <li
              key={index}
              className="bg-blue-100 text-blue-800 font-medium rounded-lg px-4 py-2 text-center hover:bg-blue-200 transition"
            >
              #{t.word} <span className="text-gray-500 text-sm">({t.frequency})</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Topic Clusters */}
      <div className="bg-white shadow-lg rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4 border-b pb-2">Detected Topics</h2>
        {Object.entries(topics).map(([topic, words]) => (
          <div key={topic} className="mb-4">
            <h3 className="font-bold text-blue-600">{topic}</h3>
            <p className="text-gray-700">{words.join(", ")}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Trending;
