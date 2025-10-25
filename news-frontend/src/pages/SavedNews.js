import React, { useEffect, useState } from "react";
import axios from "axios";
import NewsCard from "../components/NewsCard";

function SavedNews() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSaved = async () => {
      try {
        const res = await axios.get("http://127.0.0.1:8000/news/stored");
        setNews(res.data);
      } catch (error) {
        console.error("Error fetching stored news:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchSaved();
  }, []);

  if (loading) return <p className="text-center text-gray-600 mt-10">Loading...</p>;

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4 text-center text-blue-700">
        Saved Articles 📚
      </h2>
      {news.length > 0 ? (
        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-6">
          {news.map((article, i) => (
            <NewsCard key={i} article={article} />
          ))}
        </div>
      ) : (
        <p className="text-center text-gray-500 mt-10">No saved news found.</p>
      )}
    </div>
  );
}

export default SavedNews;
