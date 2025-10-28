import React, { useEffect, useState } from "react";
import { useLocation, Link, useNavigate } from "react-router-dom";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";





function ArticleDetails() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const article = state?.article;

  const [sentiment, setSentiment] = useState(null);
  const [keywords, setKeywords] = useState([]);
  const [entities, setEntities] = useState([]);
  const [error, setError] = useState("");

  const [topicTrendData, setTopicTrendData] = useState([]);
  const [topics, setTopics] = useState([]);




useEffect(() => {
  console.log("useEffect running for topic trends");
  if (!article) {
    setError("No article data found. Redirecting...");
    setTimeout(() => navigate("/"), 1500);
    return;
  }

  // Sentiment API call
  axios
    .get("http://127.0.0.1:8000/sentiment", {
      params: { text: [article.title, article.description].filter(Boolean).join(". ") }
    })
    .then(res => setSentiment(res.data.sentiment))
    .catch(() => setError("Sentiment analysis failed"));

  // Keywords API call
  axios
    .get("http://127.0.0.1:8000/extract-keywords", {
      params: { text: article.description || article.title }
    })
    .then(res => setKeywords(res.data.keywords || res.data))
    .catch(() => setError("Keyword extraction failed"));

  // NER API call
  axios
    .get("http://127.0.0.1:8000/ner", {
      params: { text: article.description || article.title }
    })
    .then(res => setEntities(res.data.entities || []))
    .catch(() => {});

  // Topic Trends API call (the new part)
  axios
    .get("http://127.0.0.1:8000/topic-trends")
    .then(res => {
      const trendData = res.data;
      if (trendData.length > 0) {
        setTopicTrendData(trendData);
        const keys = Object.keys(trendData[0]).filter(k => k !== "date");
        setTopics(keys);
      }
    })
    .catch(() => {
      console.error("Failed to load topic trend data");
    });
}, [article, navigate]);


  if (!article) return <div>Loading or redirecting...</div>;

  const sentimentColors = {
    positive: "bg-green-400",
    negative: "bg-red-400",
    neutral: "bg-yellow-400"
  };

  const scoreBar = score => ({
    width: `${Math.round(score * 100)}%`
  });

  return (
    <div className="max-w-2xl mx-auto p-5 bg-white rounded shadow">
      {/* Article Image */}
      {article.image && (
        <img
          src={article.image}
          alt={article.title}
          className="w-full rounded mb-4 object-cover"
          style={{ maxHeight: 350 }}
        />
      )}
      {/* Article Meta */}
      <div className="text-sm text-gray-600 mb-2 flex justify-between">
        <span>{article.source?.name || article.source || "Unknown source"}</span>
        <span>
          {article.publishedAt
            ? new Date(article.publishedAt).toLocaleString()
            : "Unknown date"}
        </span>
      </div>
      {/* Title */}
      <h1 className="text-2xl font-bold mb-4">{article.title}</h1>
      {/* Description */}
      <p className="mb-6">{article.description || "No description available."}</p>
      {/* External Read More Link */}
      {article.url && (
        <Link
          to={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block mb-6 px-4 py-2 bg-indigo-600 text-white rounded"
        >
          Read More
        </Link>
      )}

      {/* Sentiment */}
      <div>
        <h2 className="text-xl font-semibold mb-2">Sentiment Analysis</h2>
        {sentiment && sentiment.all_scores ? (
          <>
            {/* Sentiment Bar Visualization */}
            <div className="flex space-x-3 items-end mb-2">
              {Object.entries(sentiment.all_scores).map(([label, score]) => (
                <div key={label} className="flex-1">
                  <div
                    className={`h-4 ${sentimentColors[label.toLowerCase()] || "bg-gray-300"} rounded`}
                    style={scoreBar(score)}
                  />
                  <div className="text-xs mt-1 text-gray-600 text-center capitalize">
                    {label.toLowerCase()} {Math.round(score * 100)}%
                  </div>
                </div>
              ))}
            </div>
            {/* Final Decision Label */}
            <div>
              <span className="font-bold">{sentiment.label}</span>
              <span className="ml-2 text-gray-700">
                (Confidence: {Math.round(sentiment.confidence * 100)}%)
              </span>
            </div>
          </>
        ) : sentiment ? (
          <div>
            <strong>{sentiment.label}</strong>
            <span className="ml-2 text-gray-700">
              (Confidence: {Math.round(sentiment.confidence * 100)}%)
            </span>
          </div>
        ) : (
          <p>Loading sentiment...</p>
        )}
      </div>

      {/* Keywords */}
      <div className="mt-6">
        <h2 className="text-xl font-semibold mb-2">Extracted Keywords</h2>
        {keywords.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {keywords.map((kw, i) => (
              <span key={i} className="bg-indigo-100 text-indigo-800 rounded px-2 py-1">
                {kw.word}
                <span className="ml-2 text-xs text-gray-500">
                  ({Math.round(kw.score * 100)}%)
                </span>
              </span>
            ))}
          </div>
        ) : (
          <p>No keywords found.</p>
        )}
      </div>

      {/* NER Section */}
      <div className="mt-6">
        <h2 className="text-xl font-semibold mb-2">Named Entities</h2>
        {entities.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {entities.map((ent, i) => (
              <span
                key={i}
                className={
                  "rounded px-2 py-1 mr-1 bg-" +
                  (ent.label === "PER"
                    ? "green-200 text-green-800"
                    : ent.label === "ORG"
                    ? "yellow-200 text-yellow-900"
                    : ent.label === "LOC"
                    ? "blue-200 text-blue-800"
                    : "gray-200 text-gray-800")
                }
              >
                {ent.word} <span className="text-xs">({ent.label})</span>
              </span>
            ))}
          </div>
        ) : (
          <p>No named entities found.</p>
        )}
      </div>

    {/* Detected Topic Cluster */}
    <div className="mt-6">
      <h2 className="text-xl font-semibold mb-2">Detected Topic Cluster</h2>
      <span className="font-bold">Topic: </span>
      <span className="bg-yellow-100 text-yellow-800 rounded px-2 py-1">
        {parseInt(article.topic_id) + 1}
      </span>
      {article.topic_label
        ? <span className="ml-2 text-purple-700">({article.topic_label})</span>
        : <span className="ml-2 text-gray-500">(No keywords)</span>}
      {/* Cluster keywords */}
      {article.keywords && article.keywords.length > 0 ? (
        <div className="mt-2">
          <span className="font-bold">Cluster Keywords: </span>
          <div className="flex flex-wrap gap-2 mt-1">
            {article.keywords.map((kw, idx) => (
              <span key={idx} className="bg-purple-100 text-purple-800 rounded px-2 py-1">{kw}</span>
            ))}
          </div>
        </div>
      ) : (
        <span className="ml-2 text-gray-500">No cluster keywords found.</span>
      )}
    </div>
  </div>
)
}
export default ArticleDetails;
