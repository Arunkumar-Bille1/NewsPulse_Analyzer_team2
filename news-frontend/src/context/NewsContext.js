// src/context/NewsContext.js
import React, { createContext, useContext, useState } from "react";

const NewsContext = createContext(null);

export function NewsProvider({ children }) {
  const [news, setNews] = useState([]);        // current articles list
  const [query, setQuery] = useState("");      // current search text
  const [processedQuery, setProcessedQuery] = useState("");
  const [loading, setLoading] = useState(false);

  const value = {
    news,
    setNews,
    query,
    setQuery,
    processedQuery,
    setProcessedQuery,
    loading,
    setLoading,
  };

  return <NewsContext.Provider value={value}>{children}</NewsContext.Provider>;
}

export function useNews() {
  const ctx = useContext(NewsContext);
  if (!ctx) throw new Error("useNews must be used inside NewsProvider");
  return ctx;
}
