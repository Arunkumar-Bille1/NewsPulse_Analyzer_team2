import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import NewsCard from "../components/NewsCard";

// Voice Icon
const VoiceIcon = ({ isListening }) => (
  <svg
    className={`w-4 h-4 ${isListening ? "animate-pulse text-red-500" : "text-gray-500"}`}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
    />
  </svg>
);

// Search Icon
const SearchIcon = () => (
  <svg
    className="w-4 h-4 text-gray-400"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
    />
  </svg>
);

function Home() {
  const [news, setNews] = useState([]);
  const [query, setQuery] = useState("");
  const [processedQuery, setProcessedQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);

  const fetchNews = async (q = query) => {
    if (!q.trim()) return;
    setLoading(true);
    try {
      const res = await axios.get(`http://127.0.0.1:8000/news?query=${encodeURIComponent(q)}`);
      setNews(res.data.articles || []);
      setProcessedQuery(res.data.processed_query || "");
    } catch (e) {
      console.error(e);
      setNews([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const res = await axios.get(`http://127.0.0.1:8000/news?query=trending`);
        setNews(res.data.articles || []);
      } catch {
        setNews([]);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const startListening = () => {
    if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
      alert("Speech recognition not supported.");
      return;
    }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const rec = new SR();
    recognitionRef.current = rec;

    rec.lang = "en-US";
    rec.interimResults = false;

    rec.onresult = (e) => {
      const text = e.results[0][0].transcript;
      setQuery(text);
      fetchNews(text);
    };

    rec.onstart = () => setListening(true);
    rec.onend = () => setListening(false);

    rec.start();
  };

  const trendingTopics = ["Technology", "Business", "Sports", "Health", "Politics", "Entertainment"];

  return (
       <div className="animate-fadeIn">

      {/* CENTERED HEADER */}
      <div className="text-center mt-4">
        <h1 className="text-4xl font-bold text-gray-800">
          Discover What’s <span className="text-indigo-600">Trending</span>
        </h1>
        <p className="text-gray-600 mt-2">
          Real-time news intelligence powered by AI.
        </p>
      </div>

      {/* Search */}
      <div className="bg-white">
        <div className="max-w-6xl mx-auto px-6 py-8">
          <div className="max-w-4xl">
            <div className="flex items-center bg-white border-2 border-gray-200 rounded-2xl shadow-lg hover:border-indigo-300 transition">
              <div className="pl-5">
                <SearchIcon />
              </div>

              <input
                type="text"
                placeholder="Search breaking news, trending topics, or current events..."
                className="flex-1 px-4 py-4 outline-none bg-transparent"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />

              <button
                onClick={startListening}
                className="p-3 bg-gray-50 border border-gray-200 rounded-xl"
              >
                <VoiceIcon isListening={listening} />
              </button>

              <button
                onClick={() => fetchNews()}
                className="ml-2 bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-xl"
              >
                {loading ? "Searching..." : "Search"}
              </button>
            </div>

            {/* Trending chips */}
            <div className="mt-6 flex items-center gap-4 text-sm">
              <span className="text-gray-600">Trending:</span>
              <div className="flex gap-2 flex-wrap">
                {trendingTopics.map((topic) => (
                  <button
                    key={topic}
                    onClick={() => {
                      setQuery(topic);
                      fetchNews(topic);
                    }}
                    className="px-3 py-1.5 bg-gray-100 rounded-lg hover:bg-indigo-50 hover:text-indigo-600"
                  >
                    {topic}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="py-8">
        <div className="max-w-6xl mx-auto px-6">

          {loading && (
            <div className="flex justify-center items-center py-16">
              <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
            </div>
          )}

          {!loading && news.length > 0 && (
            <>
              <div className="flex justify-between items-end mb-6">
                <div>
                  <h2 className="text-xl font-medium text-gray-800">
                    {query ? `Results for "${processedQuery || query}"` : "Trending Stories"}
                  </h2>
                  <p className="text-sm text-gray-600">{news.length} articles found</p>
                </div>

                {query && (
                  <button className="text-indigo-600" onClick={() => setQuery("")}>
                    Clear search
                  </button>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {news.map((article, index) => (
                  <NewsCard key={index} article={article} />
                ))}
              </div>
            </>
          )}
        </div>
      </div>
      {/* LIGHTER footer */}
      <footer className="bg-white border-t border-gray-100">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="text-center text-sm text-gray-500">
            <span className="font-medium text-gray-700">TrendVista</span> © 2025 · All rights reserved
          </div>
        </div>
      </footer>
    </div>
  );
}

export default Home;
