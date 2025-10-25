import React from "react";

function NewsCard({ article, keywords = [] }) {
  // Simple date formatting
  const formatDate = (dateString) => {
    try {
      if (!dateString) return "Unknown date";
      const date = new Date(dateString);
      const now = new Date();
      const diffHours = Math.floor(Math.abs(now - date) / (1000 * 60 * 60));
      
      if (diffHours < 1) return "Just now";
      if (diffHours < 24) return `${diffHours}h ago`;
      if (diffHours < 48) return "Yesterday";
      
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
      });
    } catch (error) {
      return "Unknown date";
    }
  };

  const formatTime = (dateString) => {
    try {
      if (!dateString) return "";
      const date = new Date(dateString);
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      });
    } catch (error) {
      return "";
    }
  };

  return (
    <div className="group bg-white rounded-lg shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100 hover:border-indigo-200 hover:-translate-y-1">
      
      {/* Image Section */}
      <div className="relative h-48 overflow-hidden bg-gray-100">
        {article.image ? (
          <img
            src={article.image}
            alt={article.title || "News article"}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            onError={(e) => {
              e.target.src = "https://via.placeholder.com/400x200/6366f1/white?text=TrendVista";
            }}
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <span className="text-white font-semibold text-lg">TrendVista</span>
          </div>
        )}

        {/* Source Badge */}
        {article.source && (
          <div className="absolute top-3 right-3">
            <span className="bg-black/70 text-white text-xs px-3 py-1 rounded-full">
              {typeof article.source === 'object' ? article.source.name : article.source}
            </span>
          </div>
        )}
      </div>

      {/* Content Section */}
      <div className="p-5">
        
        {/* Title */}
        <h3 className="font-bold text-lg text-gray-900 mb-3 leading-tight line-clamp-2 hover:text-indigo-700 transition-colors">
          {article.title || "No title available"}
        </h3>

        {/* Description */}
        <p className="text-sm text-gray-600 mb-4 leading-relaxed line-clamp-2">
          {article.description || "Stay updated with the latest news and breaking stories."}
        </p>

        {/* Keywords (only if available) */}
        {(article.keywords?.length > 0 || keywords.length > 0) && (
          <div className="mb-4">
            <div className="flex flex-wrap gap-2">
              {(article.keywords || keywords).slice(0, 2).map((keyword, index) => {
                const keywordText = typeof keyword === 'string' ? keyword : keyword.keyword;
                return (
                  <span
                    key={index}
                    className="bg-indigo-50 text-indigo-700 text-xs px-2 py-1 rounded-full"
                  >
                    {keywordText}
                  </span>
                );
              })}
            </div>
          </div>
        )}

        {/* Bottom Section - Date/Time and Button */}
        <div className="flex items-center justify-between">
          
          {/* Date & Time */}
          <div className="text-xs text-gray-500">
            <div className="font-medium text-gray-700">{formatDate(article.publishedAt)}</div>
            <div>{formatTime(article.publishedAt)}</div>
          </div>

          {/* Attractive Read More Button */}
          {article.url && (
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="group/btn inline-flex items-center bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200 hover:scale-105"
            >
              Read More
              <svg 
                className="w-4 h-4 ml-1 group-hover/btn:translate-x-1 transition-transform duration-200" 
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

      {/* Bottom accent line */}
      <div className="h-1 bg-gradient-to-r from-indigo-500 to-purple-500 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300"></div>
    </div>
  );
}

export default NewsCard;
