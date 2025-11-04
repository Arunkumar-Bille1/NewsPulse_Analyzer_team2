import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import NewsCard from "../components/NewsCard";

// Voice Icon
const VoiceIcon = ({ isListening }) => (
  <svg
    className={`w-4 h-4 ${isListening ? 'animate-pulse text-red-500' : 'text-gray-500'}`}
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

  const fetchNews = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const response = await axios.get(`http://127.0.0.1:8000/news?query=${query}`);
      setNews(response.data.articles);
      setProcessedQuery(response.data.processed_query || "");
    } catch (error) {
      console.error("Error fetching news", error);
      setNews([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const fetchDefaultNews = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`http://127.0.0.1:8000/news?query=trending`);
        setNews(response.data.articles);
      } catch (error) {
        console.error("Error fetching default news", error);
        setNews([]);
      } finally {
        setLoading(false);
      }
    };
    fetchDefaultNews();
  }, []);

  const startListening = () => {
    if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
      alert("Speech recognition is not supported in this browser.");
      return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.lang = "en-US";
    recognitionRef.current.interimResults = false;
    recognitionRef.current.maxAlternatives = 1;

    recognitionRef.current.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setQuery(transcript);
      setListening(false);
    };

    recognitionRef.current.onstart = () => setListening(true);
    recognitionRef.current.onend = () => setListening(false);
    recognitionRef.current.onerror = (event) => {
      setListening(false);
      alert("Speech recognition error: " + event.error);
    };

    recognitionRef.current.start();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      fetchNews();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section with lighter, smaller typography */}
      <div className="bg-white">
        <div className="max-w-5xl mx-auto px-6 py-12">
          <div className="max-w-3xl">
            {/* SMALLER AND LESS BOLD HEADING */}
            <h1 className="text-3xl md:text-4xl font-semibold text-gray-800 mb-3 leading-tight">
              Discover What's <span className="text-indigo-600 font-medium">Trending</span>
            </h1>
            {/* SMALLER AND LIGHTER SUBTITLE */}
            <p className="text-base text-gray-600 mb-8 leading-relaxed font-normal">
              Real-time news intelligence powered by AI. Stay informed with the stories that matter.
            </p>
          </div>
          
          <div className="max-w-4xl">
            <div className="relative">
              <div className="flex items-center bg-white border-2 border-gray-200 rounded-2xl shadow-lg hover:border-indigo-300 focus-within:border-indigo-500 focus-within:shadow-xl transition-all duration-300">
                <div className="flex-1 flex items-center min-w-0">
                  <div className="pl-5 flex-shrink-0">
                    <SearchIcon />
                  </div>
                  <input
                    type="text"
                    placeholder="Search breaking news, trending topics, or current events..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={handleKeyPress}
                    className="w-full px-4 py-4 text-sm font-normal placeholder-gray-400 border-none focus:outline-none bg-transparent"
                  />
                </div>
                
                <div className="flex items-center space-x-2 pr-3">
                  <button
                    onClick={startListening}
                    disabled={listening}
                    className={`p-3 rounded-xl transition-all duration-300 border ${
                      listening 
                        ? 'bg-red-50 border-red-200 text-red-600' 
                        : 'bg-gray-50 border-gray-200 hover:bg-gray-100 text-gray-500'
                    }`}
                    title={listening ? 'Listening...' : 'Voice search'}
                  >
                    <VoiceIcon isListening={listening} />
                  </button>
                  
                  <button
                    onClick={fetchNews}
                    disabled={!query.trim() || loading}
                    className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white px-6 py-3 rounded-xl text-sm font-medium transition-all duration-300 shadow-lg hover:shadow-xl disabled:shadow-sm"
                  >
                    {loading ? 'Searching...' : 'Search'}
                  </button>
                </div>
              </div>
            </div>
            
            {/* SMALLER trending topics */}
            <div className="mt-6">
              <div className="flex items-center space-x-4 text-sm">
                <span className="text-gray-600 font-normal">Trending:</span>
                <div className="flex flex-wrap gap-2">
                  {['Technology', 'Business', 'Sports', 'Health', 'Politics', 'Entertainment'].map((topic) => (
                    <button
                      key={topic}
                      onClick={() => {
                        setQuery(topic);
                        setTimeout(() => fetchNews(), 100);
                      }}
                      className="px-3 py-1.5 bg-gray-100 hover:bg-indigo-50 hover:text-indigo-700 text-gray-700 rounded-lg text-sm font-normal transition-colors duration-200 border border-transparent hover:border-indigo-200"
                    >
                      {topic}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Results section with lighter typography */}
      <div className="bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-6">
          {loading && (
            <div className="flex flex-col items-center justify-center py-16">
              <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mb-4"></div>
              <p className="text-gray-600 font-normal text-sm">Finding the latest stories for you...</p>
            </div>
          )}

          {!loading && news.length > 0 && (
            <div className="space-y-6">
              {/* SMALLER AND LIGHTER results header */}
              <div className="flex items-end justify-between">
                <div>
                  <h2 className="text-xl font-medium text-gray-800 mb-1">
                    {query ? `Results for "${processedQuery}"` : 'Trending Stories'}
                  </h2>
                  <p className="text-gray-600 text-sm font-normal">
                    {news.length} {news.length === 1 ? 'article' : 'articles'} found
                  </p>
                </div>
                {query && (
                  <button
                    onClick={() => {
                      setQuery('');
                      setTimeout(() => fetchNews(), 100);
                    }}
                    className="text-sm text-indigo-600 hover:text-indigo-700 font-normal"
                  >
                    Clear search
                  </button>
                )}
              </div>
              
              {/* ENHANCED NEWS CARDS WITH HOVER EFFECTS */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {news.map((article, index) => (
                  <div 
                    key={index} 
                    className="hover:shadow-lg hover:-translate-y-1 transition-all duration-300 cursor-pointer"
                  >
                    <NewsCard article={article} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {!loading && news.length === 0 && query && (
            <div className="text-center py-16">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-800 mb-2">No articles found</h3>
              <p className="text-gray-600 mb-6 max-w-md mx-auto text-sm font-normal">
                We couldn't find any articles matching your search. Try different keywords or browse our trending topics.
              </p>
              <div className="space-x-4">
                <button
                  onClick={() => {
                    setQuery('');
                    setTimeout(() => fetchNews(), 100);
                  }}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg text-sm font-medium transition-colors duration-200"
                >
                  Browse Trending
                </button>
                <button
                  onClick={() => setQuery('')}
                  className="text-indigo-600 hover:text-indigo-700 text-sm font-normal"
                >
                  Clear search
                </button>
              </div>
            </div>
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
