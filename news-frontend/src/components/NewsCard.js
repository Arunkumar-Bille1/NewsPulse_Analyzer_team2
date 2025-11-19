import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { addBookmark, removeBookmark, checkBookmark } from "../api";
import { Bookmark, BookmarkCheck } from "lucide-react";

function NewsCard({ article, keywords = [] }) {
  const navigate = useNavigate();

  const [isBookmarked, setIsBookmarked] = useState(false);
  const userEmail = localStorage.getItem("user_email"); // raw email

  /** -----------------------------
   * CHECK IF BOOKMARKED
   ----------------------------- */
  useEffect(() => {
    if (!userEmail || !article.url) return;

    const check = async () => {
      try {
        const res = await checkBookmark(userEmail, article.url);
        setIsBookmarked(res.data.bookmarked);
      } catch (err) {
        console.log("Bookmark check error:", err);
      }
    };

    check();
  }, [article.url, userEmail]);

  /** -----------------------------
   * ADD / REMOVE BOOKMARK
   ----------------------------- */
  const toggleBookmark = async () => {
    if (!userEmail) {
      alert("Please login to bookmark articles.");
      return;
    }

    try {
      if (isBookmarked) {
        // remove
        await removeBookmark(userEmail, article.url);
        setIsBookmarked(false);
      } else {
        // save
        await addBookmark(userEmail, article);
        setIsBookmarked(true);
      }
    } catch (err) {
      console.log("❌ Bookmark toggle error:", err);
    }
  };

  /** -----------------------------
   * DATE FORMAT
   ----------------------------- */
  const formatDate = (dateString) => {
    try {
      if (!dateString) return "Unknown date";
      const date = new Date(dateString);
      const now = new Date();
      const diffHours = Math.floor(Math.abs(now - date) / (1000 * 60 * 60));

      if (diffHours < 1) return "Just now";
      if (diffHours < 24) return `${diffHours}h ago`;
      if (diffHours < 48) return "Yesterday";

      return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year:
          date.getFullYear() !== now.getFullYear()
            ? "numeric"
            : undefined,
      });
    } catch {
      return "Unknown date";
    }
  };

  const formatTime = (dateString) => {
    try {
      if (!dateString) return "";
      const date = new Date(dateString);
      return date.toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: true,
      });
    } catch {
      return "";
    }
  };

  /** -----------------------------
   * VIEW DETAILS
   ----------------------------- */
  const handleViewArticle = () => {
    navigate(`/article/${encodeURIComponent(article.url)}`, {
      state: { article },
    });
  };

  return (
    <div className="group bg-white rounded-lg shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100 hover:border-indigo-200 hover:-translate-y-1">
      
      {/* IMAGE SECTION */}
      <div className="relative h-48 overflow-hidden bg-gray-100">
        {article.image ? (
          <img
            src={article.image}
            alt={article.title || "News"}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            onError={(e) =>
              (e.target.src =
                "https://via.placeholder.com/400x200/6366f1/white?text=TrendVista")
            }
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <span className="text-white font-semibold text-lg">
              TrendVista
            </span>
          </div>
        )}

        {/* SOURCE BADGE */}
        {article.source && (
          <div className="absolute top-3 right-3">
            <span className="bg-black/70 text-white text-xs px-3 py-1 rounded-full">
              {typeof article.source === "object"
                ? article.source.name
                : article.source}
            </span>
          </div>
        )}

        {/* ⭐ BOOKMARK BUTTON */}
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

      {/* CONTENT SECTION */}
      <div className="p-5">
        <h3 className="font-bold text-lg text-gray-900 mb-3 line-clamp-2 hover:text-indigo-700 transition-colors">
          {article.title || "No title available"}
        </h3>

        <p className="text-sm text-gray-600 mb-4 line-clamp-2">
          {article.description ||
            "Stay updated with the latest news and breaking stories."}
        </p>

        {/* KEYWORDS */}
        {(article.keywords?.length > 0 || keywords.length > 0) && (
          <div className="mb-4 flex flex-wrap gap-2">
            {(article.keywords || keywords)
              .slice(0, 2)
              .map((keyword, idx) => {
                const kw = typeof keyword === "string" ? keyword : keyword.keyword;
                return (
                  <span
                    key={idx}
                    className="bg-indigo-50 text-indigo-700 text-xs px-2 py-1 rounded-full"
                  >
                    {kw}
                  </span>
                );
              })}
          </div>
        )}

        {/* BOTTOM SECTION */}
        <div className="flex items-center justify-between">
          <div className="text-xs text-gray-500">
            <div className="font-medium text-gray-700">
              {formatDate(article.publishedAt)}
            </div>
            <div>{formatTime(article.publishedAt)}</div>
          </div>

          {/* VIEW BUTTON */}
          <button
            className="ml-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded transition"
            onClick={handleViewArticle}
          >
            View Article
          </button>

          {/* READ MORE BUTTON */}
          {article.url && (
            <a
              href={article.url}
              target="_blank"
              rel="noreferrer"
              className="ml-2 inline-flex items-center bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm transition-all duration-200 hover:scale-105"
            >
              Read More
              <svg
                className="w-4 h-4 ml-1 transition-transform group-hover:translate-x-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 8l4 4m0 0l-4 4m4-4H3"
                />
              </svg>
            </a>
          )}
        </div>
      </div>

      {/* HOVER LINE */}
      <div className="h-1 bg-gradient-to-r from-indigo-500 to-purple-500 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300"></div>
    </div>
  );
}

export default NewsCard;
