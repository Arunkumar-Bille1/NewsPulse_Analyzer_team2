import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { addBookmark, removeBookmark } from "../api";
import { Bookmark, BookmarkCheck } from "lucide-react";

export default function NewsCard({ article, keywords = [], isSaved = false }) {
  const navigate = useNavigate();
  const userEmail = localStorage.getItem("user_email");

  const [isBookmarked, setIsBookmarked] = useState(isSaved);

  /** ---------------------------------------------------
   * UNIVERSAL SAFE IMAGE HANDLER (Fixes 403 + broken URLs)
   -----------------------------------------------------*/
  const fallbackImg = "https://placehold.co/600x400?text=No+Image";

  const getImage = () => {
    const raw =
      article.image ||
      article.urlToImage ||
      article.image_url ||
      article.thumbnail ||
      article.img ||
      article.picture;

    if (!raw) return fallbackImg;

    // 🔥 Proxy to prevent 403/blocked images
    return `https://images.weserv.nl/?url=${encodeURIComponent(raw)}`;
  };

  /** ---------------------------------------------------
   * BOOKMARK TOGGLE
   -----------------------------------------------------*/
  const toggleBookmark = async () => {
    if (!userEmail) {
      alert("Please login to bookmark articles.");
      return;
    }

    try {
      if (isBookmarked) {
        await removeBookmark(userEmail, article.url);
        setIsBookmarked(false);
      } else {
        await addBookmark(userEmail, article);
        setIsBookmarked(true);
      }
    } catch (err) {
      console.log("Bookmark error:", err);
    }
  };

  /** ---------------------------------------------------
   * DATE FORMATTERS
   -----------------------------------------------------*/
  const formatDate = (date) => {
    if (!date) return "Unknown date";

    const d = new Date(date);
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const formatTime = (date) => {
    if (!date) return "";
    return new Date(date).toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  /** ---------------------------------------------------
   * VIEW DETAILS
   -----------------------------------------------------*/
  const handleViewArticle = () => {
    navigate(`/article/${encodeURIComponent(article.url)}`, {
      state: { article },
    });
  };

  return (
    <div className="group bg-white rounded-lg shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100 hover:border-indigo-300 hover:-translate-y-1">

      {/* IMAGE */}
      <div className="relative h-48 overflow-hidden bg-gray-100">
        <img
          src={getImage()}
          alt={article.title || "News"}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          onError={(e) => (e.target.src = fallbackImg)}
        />

        {/* SOURCE */}
        {article.source && (
          <div className="absolute top-3 right-3">
            <span className="bg-black/70 text-white text-xs px-3 py-1 rounded-full">
              {typeof article.source === "object"
                ? article.source.name
                : article.source}
            </span>
          </div>
        )}

        {/* BOOKMARK BUTTON */}
        <button
          onClick={toggleBookmark}
          className="absolute top-3 left-3 bg-white/80 backdrop-blur-sm p-2 rounded-full shadow-md hover:bg-white transition"
        >
          {isBookmarked ? (
            <BookmarkCheck className="w-5 h-5 text-indigo-600" />
          ) : (
            <Bookmark className="w-5 h-5 text-gray-700" />
          )}
        </button>
      </div>

      {/* CONTENT */}
      <div className="p-5">
        <h3 className="font-bold text-lg text-gray-900 mb-3 line-clamp-2 hover:text-indigo-700 transition-colors">
          {article.title || "No title available"}
        </h3>

        <p className="text-sm text-gray-600 mb-4 line-clamp-2">
          {article.description || "No description available."}
        </p>

        {/* KEYWORDS */}
        {(article.keywords?.length > 0 || keywords.length > 0) && (
          <div className="mb-4 flex flex-wrap gap-2">
            {(article.keywords || keywords)
              .slice(0, 2)
              .map((kw, idx) => (
                <span
                  key={idx}
                  className="bg-indigo-50 text-indigo-700 text-xs px-2 py-1 rounded-full"
                >
                  {typeof kw === "string" ? kw : kw.keyword}
                </span>
              ))}
          </div>
        )}

        {/* FOOTER */}
        <div className="flex items-center justify-between">
          <div className="text-xs text-gray-500">
            <div className="font-medium text-gray-700">
              {formatDate(article.publishedAt)}
            </div>
            <div>{formatTime(article.publishedAt)}</div>
          </div>

          <button
            onClick={handleViewArticle}
            className="ml-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded transition"
          >
            View
          </button>

          {article.url && (
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="ml-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm hover:scale-105 transition"
            >
              Read More →
            </a>
          )}
        </div>
      </div>

      {/* HOVER LINE */}
      <div className="h-1 bg-gradient-to-r from-indigo-500 to-purple-600 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300"></div>
    </div>
  );
}
