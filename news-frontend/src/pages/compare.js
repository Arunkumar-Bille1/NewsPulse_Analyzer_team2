// src/pages/compare.js
import React, { useState, useMemo, useRef } from "react";
import { searchArticles } from "../api";

/* ===========================
   Simple Sentiment (rule-based)
   =========================== */
const positiveWords = [
  "good",
  "great",
  "excellent",
  "positive",
  "growth",
  "win",
  "success",
  "benefit",
  "improve",
  "gain",
  "optimistic",
  "strong"
];
const negativeWords = [
  "bad",
  "poor",
  "decline",
  "loss",
  "negative",
  "fail",
  "risk",
  "weak",
  "drop",
  "concern",
  "worse"
];

function sentimentAnalysis(text = "") {
  if (!text) return 0;
  const t = text.toLowerCase();
  let score = 0;
  positiveWords.forEach((w) => (t.includes(w) ? (score += 1) : null));
  negativeWords.forEach((w) => (t.includes(w) ? (score -= 1) : null));
  return score; // integer
}

/* ===========================
   Keyword extraction (simple freq)
   =========================== */
const STOPWORDS = new Set([
  "the","is","in","at","of","and","a","to","for","on","with","as","by","an","be","are","that","from","this","it","was","which","or","has","have","its","will","their","they","but","not","who","were","been","he","she","we","you","i"
]);

function extractKeywords(text = "", topN = 8) {
  if (!text) return [];
  const cleaned = text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter((w) => w && !STOPWORDS.has(w) && w.length > 2);

  const freq = {};
  cleaned.forEach((w) => (freq[w] = (freq[w] || 0) + 1));
  const sorted = Object.entries(freq).sort((a, b) => b[1] - a[1]);
  return sorted.slice(0, topN).map((s) => s[0]);
}

/* ===========================
   Cosine similarity (TF vectors)
   =========================== */
function textToVector(text = "") {
  const tokens = text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter((t) => t && !STOPWORDS.has(t) && t.length > 1);
  const tf = {};
  tokens.forEach((t) => (tf[t] = (tf[t] || 0) + 1));
  return tf;
}
function cosineSimilarity(textA = "", textB = "") {
  if (!textA || !textB) return 0;
  const vA = textToVector(textA);
  const vB = textToVector(textB);
  const intersection = Object.keys(vA).filter((k) => vB[k]);
  let dot = 0;
  intersection.forEach((k) => {
    dot += vA[k] * vB[k];
  });
  const magA = Math.sqrt(Object.values(vA).reduce((s, n) => s + n * n, 0));
  const magB = Math.sqrt(Object.values(vB).reduce((s, n) => s + n * n, 0));
  if (magA === 0 || magB === 0) return 0;
  const cos = dot / (magA * magB);
  return Math.round(cos * 100); // percent similarity (0-100)
}

/* ===========================
   Tone classification (rule-based)
   =========================== */
const angerWords = ["angry", "outrage", "furious", "angst", "rage", "uproar"];
const joyWords = ["happy", "joy", "celebrate", "delight", "pleased", "excited"];
function classifyTone(text = "") {
  const t = (text || "").toLowerCase();
  let score = sentimentAnalysis(t);
  let tone = "Neutral";
  if (score > 1) tone = "Positive";
  if (score < -1) tone = "Negative";

  // emotion overrides
  for (const w of angerWords) if (t.includes(w)) return "Angry";
  for (const w of joyWords) if (t.includes(w)) return "Joyful";
  return tone;
}

/* ===========================
   UI Component
   =========================== */
export default function Compare() {
  const [searchText, setSearchText] = useState("");
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false); // full-screen loading
  const [buttonSearching, setButtonSearching] = useState(false); // changes button text

  const [article1, setArticle1] = useState(null);
  const [article2, setArticle2] = useState(null);

  const [popupText, setPopupText] = useState("");
  const [showPopup, setShowPopup] = useState(false);

  // UI: full-screen side-by-side compare view open when two selected
  const [viewMode, setViewMode] = useState("grid"); // 'grid' or 'side-by-side'
  const [activeTab, setActiveTab] = useState("overview"); // overview/sentiment/keywords

  const compareRef = useRef(null);
  const fallbackImg =
    "https://via.placeholder.com/800x450.png?text=No+Image+Available";

  /* ----- Search handler with loading UX ----- */
  const handleSearch = async () => {
    if (!searchText.trim()) return;
    setButtonSearching(true); // button shows 'Searching...'
    setLoading(true); // show full-screen loader & shimmer
    try {
      const res = await searchArticles(searchText);
      // simulate slight delay for demo polish (remove if you want)
      await new Promise((r) => setTimeout(r, 500));
      setArticles(res.articles || []);
    } catch (err) {
      console.error("search error", err);
      setPopup("Search failed. Try again.");
    } finally {
      setButtonSearching(false);
      setLoading(false);
    }
  };

  /* ----- popup helper ----- */
  const setPopup = (msg, ms = 1800) => {
    setPopupText(msg);
    setShowPopup(true);
    setTimeout(() => setShowPopup(false), ms);
  };

  /* ----- compare button behavior ----- */
  const handleCompareClick = (article) => {
    if (!article1) {
      setArticle1(article);
      setPopup("Left article added. Now select the right article.");
      return;
    }
    if (!article2) {
      // prevent same article twice
      if (article.url === article1.url) {
        setPopup("Please select a different article as the right article.");
        return;
      }
      setArticle2(article);
      setPopup("Right article added — opening full comparison...");
      // open side-by-side view
      setTimeout(() => {
        setViewMode("side-by-side");
        setActiveTab("overview");
      }, 800);
      return;
    }
    setPopup("Two articles already selected. Clear to start again.");
  };

  const clearSelection = () => {
    setArticle1(null);
    setArticle2(null);
    setViewMode("grid");
    setActiveTab("overview");
  };

  /* ----- Derived analysis values (memoized) ----- */
  const combinedText1 = useMemo(
    () => `${article1?.title || ""} ${article1?.description || ""} ${article1?.content || ""}`,
    [article1]
  );
  const combinedText2 = useMemo(
    () => `${article2?.title || ""} ${article2?.description || ""} ${article2?.content || ""}`,
    [article2]
  );

  const similarity = useMemo(() => {
    if (!article1 || !article2) return 0;
    return cosineSimilarity(combinedText1, combinedText2);
  }, [combinedText1, combinedText2, article1, article2]);

  const keywords1 = useMemo(() => extractKeywords(combinedText1, 8), [combinedText1]);
  const keywords2 = useMemo(() => extractKeywords(combinedText2, 8), [combinedText2]);

  const sentiment1 = useMemo(() => sentimentAnalysis(combinedText1), [combinedText1]);
  const sentiment2 = useMemo(() => sentimentAnalysis(combinedText2), [combinedText2]);

  const tone1 = useMemo(() => classifyTone(combinedText1), [combinedText1]);
  const tone2 = useMemo(() => classifyTone(combinedText2), [combinedText2]);

  /* ----- Export: download PNG/PDF using dynamic import (html2canvas & jspdf) ----- */
  const handleExportPNG = async () => {
    try {
      const html2canvas = (await import("html2canvas")).default;
      if (!compareRef.current) return setPopup("Nothing to export.");
      const canvas = await html2canvas(compareRef.current, { scale: 2 });
      const url = canvas.toDataURL("image/png");
      const a = document.createElement("a");
      a.href = url;
      a.download = "comparison.png";
      document.body.appendChild(a);
      a.click();
      a.remove();
      setPopup("PNG downloaded.");
    } catch (err) {
      console.error(err);
      setPopup("Export to PNG failed. (install html2canvas?)");
    }
  };

  const handleExportPDF = async () => {
    try {
      const html2canvas = (await import("html2canvas")).default;
      const { jsPDF } = await import("jspdf");
      if (!compareRef.current) return setPopup("Nothing to export.");
      const canvas = await html2canvas(compareRef.current, { scale: 2 });
      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF("landscape", "pt", "a4");
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
      pdf.addImage(imgData, "PNG", 0, 20, pdfWidth, pdfHeight);
      pdf.save("comparison.pdf");
      setPopup("PDF downloaded.");
    } catch (err) {
      console.error(err);
      setPopup("Export to PDF failed. (install html2canvas & jspdf?)");
    }
  };

  /* ----- Render helpers ----- */
  const renderArticleCard = (a, i) => (
    <div key={i} className="bg-white dark:bg-slate-800 border rounded-xl shadow hover:shadow-lg transition overflow-hidden">
      <img
        src={a.urlToImage || a.image || a.urlToImageUrl || fallbackImg}
        alt={a.title}
        className="w-full h-44 object-cover"
      />
      <div className="p-4">
        <h3 className="font-semibold text-gray-800 dark:text-gray-100 text-lg">{a.title}</h3>
        <p className="text-sm text-gray-500 dark:text-gray-300 mt-2 line-clamp-3">
          {a.description || (a.content ? a.content.slice(0, 120) + "..." : "No description available.")}
        </p>
        <div className="mt-4 flex gap-2">
          <button
            onClick={() => handleCompareClick(a)}
            className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg"
          >
            Compare
          </button>
          <a
            href={a.url}
            target="_blank"
            rel="noreferrer"
            className="px-4 py-2 border rounded-lg text-sm text-indigo-600 hover:underline"
          >
            Read
          </a>
        </div>
      </div>
    </div>
  );

  /* ----- Shimmer placeholder while loading ----- */
  const ShimmerCard = () => (
    <div className="bg-white border rounded-xl overflow-hidden animate-pulse h-56" />
  );

  /* ===========================
     JSX
     =========================== */
  return (
    <div className="p-6 min-h-screen bg-gray-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 transition-colors">
      {/* Popup */}
      {showPopup && (
        <div className="fixed top-6 left-1/2 -translate-x-1/2 z-50">
          <div className="bg-indigo-600 text-white px-5 py-3 rounded-xl shadow">{popupText}</div>
        </div>
      )}

      {/* Full-screen loading overlay */}
      {loading && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/30">
          <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-lg flex flex-col items-center gap-4">
            <div className="loader w-14 h-14 border-4 border-indigo-600 border-dashed rounded-full animate-spin" />
            <div className="text-gray-700 dark:text-gray-200">Loading results…</div>
          </div>
        </div>
      )}

      {/* Header / search */}
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-4 mb-6">
          <h1 className="text-3xl font-extrabold">Compare <span className="text-indigo-600">Articles</span></h1>

          <div className="ml-auto flex gap-2 items-center">
            <button
              onClick={() => {
                if (article1 && article2) {
                  setViewMode(viewMode === "grid" ? "side-by-side" : "grid");
                } else {
                  setPopup("Select two articles to open full comparison.");
                }
              }}
              className="px-3 py-2 border rounded-lg text-sm"
            >
              {viewMode === "grid" ? "Open Side-by-Side" : "Back to Grid"}
            </button>

            <button
              onClick={clearSelection}
              className="px-3 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Search bar */}
        <div className="flex items-center gap-3 mb-6">
          <input
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="Search news articles..."
            className="flex-1 p-3 rounded-full border outline-none bg-white dark:bg-slate-800"
          />

          <button
            onClick={handleSearch}
            disabled={buttonSearching}
            className={`px-6 py-2 rounded-full text-white ${buttonSearching ? "bg-indigo-400" : "bg-indigo-600 hover:bg-indigo-700"}`}
          >
            {buttonSearching ? "Searching..." : "Search"}
          </button>
        </div>

        {/* Grid view of articles */}
        {viewMode === "grid" && (
          <>
            {articles.length === 0 ? (
              <div className="text-center text-gray-500 mt-12">No articles. Use the search box above.</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {loading
                  ? Array.from({ length: 6 }).map((_, i) => <ShimmerCard key={i} />)
                  : articles.map(renderArticleCard)}
              </div>
            )}
          </>
        )}

        {/* SIDE-BY-SIDE comparison view */}
        {viewMode === "side-by-side" && (
          <div className="mt-6" ref={compareRef}>
            <div className="flex gap-6">
              {/* LEFT ARTICLE */}
              <div className="w-1/2 bg-white dark:bg-slate-800 rounded-xl p-4 shadow">
                <div className="flex gap-4">
                  <img
                    src={article1?.urlToImage || article1?.image || article1?.urlToImageUrl || fallbackImg}
                    alt=""
                    className="w-40 h-24 object-cover rounded-md"
                  />
                  <div>
                    <h3 className="font-semibold text-lg">{article1?.title}</h3>
                    <p className="text-xs text-gray-500 dark:text-gray-300 mt-1">Source: {article1?.source?.name || "Unknown"}</p>
                    <p className="text-xs text-gray-400 mt-2">Tone: <strong>{tone1}</strong></p>
                    <p className="text-xs text-gray-400">Sentiment: <strong>{sentiment1}</strong></p>
                  </div>
                </div>

                <div className="mt-4 text-sm text-gray-700 dark:text-gray-200">
                  {article1?.description || article1?.content || "No description available."}
                </div>

                {/* keywords */}
                <div className="mt-4">
                  <h4 className="text-sm font-medium">Keywords</h4>
                  <div className="flex gap-2 flex-wrap mt-2">
                    {keywords1.length ? keywords1.map((k) => (
                      <span key={k} className="px-2 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs">{k}</span>
                    )) : <span className="text-xs text-gray-400">No keywords</span>}
                  </div>
                </div>
              </div>

              {/* RIGHT ARTICLE */}
              <div className="w-1/2 bg-white dark:bg-slate-800 rounded-xl p-4 shadow">
                <div className="flex gap-4">
                  <img
                    src={article2?.urlToImage || article2?.image || article2?.urlToImageUrl || fallbackImg}
                    alt=""
                    className="w-40 h-24 object-cover rounded-md"
                  />
                  <div>
                    <h3 className="font-semibold text-lg">{article2?.title}</h3>
                    <p className="text-xs text-gray-500 dark:text-gray-300 mt-1">Source: {article2?.source?.name || "Unknown"}</p>
                    <p className="text-xs text-gray-400 mt-2">Tone: <strong>{tone2}</strong></p>
                    <p className="text-xs text-gray-400">Sentiment: <strong>{sentiment2}</strong></p>
                  </div>
                </div>

                <div className="mt-4 text-sm text-gray-700 dark:text-gray-200">
                  {article2?.description || article2?.content || "No description available."}
                </div>

                {/* keywords */}
                <div className="mt-4">
                  <h4 className="text-sm font-medium">Keywords</h4>
                  <div className="flex gap-2 flex-wrap mt-2">
                    {keywords2.length ? keywords2.map((k) => (
                      <span key={k} className="px-2 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs">{k}</span>
                    )) : <span className="text-xs text-gray-400">No keywords</span>}
                  </div>
                </div>
              </div>
            </div>

            {/* TABS: Overview / Sentiment / Keywords */}
            <div className="mt-6 bg-white dark:bg-slate-800 rounded-xl p-4 shadow">
              <div className="flex items-center justify-between">
                <div className="flex gap-2">
                  <button onClick={() => setActiveTab("overview")} className={`px-3 py-1 rounded ${activeTab === "overview" ? "bg-indigo-600 text-white" : "bg-gray-100 dark:bg-slate-700"}`}>Overview</button>
                  <button onClick={() => setActiveTab("sentiment")} className={`px-3 py-1 rounded ${activeTab === "sentiment" ? "bg-indigo-600 text-white" : "bg-gray-100 dark:bg-slate-700"}`}>Sentiment</button>
                  <button onClick={() => setActiveTab("keywords")} className={`px-3 py-1 rounded ${activeTab === "keywords" ? "bg-indigo-600 text-white" : "bg-gray-100 dark:bg-slate-700"}`}>Keywords</button>
                </div>

                <div className="flex gap-2 items-center">
                  <div className="text-sm text-gray-600 dark:text-gray-300">Similarity: <strong>{similarity}%</strong></div>
                  <button onClick={handleExportPNG} className="px-3 py-1 bg-green-600 text-white rounded text-sm">Download PNG</button>
                  <button onClick={handleExportPDF} className="px-3 py-1 bg-blue-600 text-white rounded text-sm">Download PDF</button>
                </div>
              </div>

              <div className="mt-4">
                {activeTab === "overview" && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold">Article 1 — Overview</h4>
                      <p className="text-sm text-gray-700 dark:text-gray-300 mt-2">{combinedText1 || "No content"}</p>
                    </div>
                    <div>
                      <h4 className="font-semibold">Article 2 — Overview</h4>
                      <p className="text-sm text-gray-700 dark:text-gray-300 mt-2">{combinedText2 || "No content"}</p>
                    </div>
                  </div>
                )}

                {activeTab === "sentiment" && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 bg-gray-50 dark:bg-slate-700 rounded">
                      <h4 className="font-semibold">Article 1 Sentiment</h4>
                      <p className="mt-2">Score: <strong>{sentiment1}</strong></p>
                      <p className="mt-1">Tone: <strong>{tone1}</strong></p>
                    </div>
                    <div className="p-4 bg-gray-50 dark:bg-slate-700 rounded">
                      <h4 className="font-semibold">Article 2 Sentiment</h4>
                      <p className="mt-2">Score: <strong>{sentiment2}</strong></p>
                      <p className="mt-1">Tone: <strong>{tone2}</strong></p>
                    </div>
                  </div>
                )}

                {activeTab === "keywords" && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 bg-gray-50 dark:bg-slate-700 rounded">
                      <h4 className="font-semibold">Article 1 Keywords</h4>
                      <div className="flex gap-2 flex-wrap mt-2">
                        {keywords1.length ? keywords1.map((k) => <span key={k} className="px-2 py-1 bg-indigo-50 text-indigo-700 rounded">{k}</span>) : <span className="text-xs text-gray-400">No keywords</span>}
                      </div>
                    </div>
                    <div className="p-4 bg-gray-50 dark:bg-slate-700 rounded">
                      <h4 className="font-semibold">Article 2 Keywords</h4>
                      <div className="flex gap-2 flex-wrap mt-2">
                        {keywords2.length ? keywords2.map((k) => <span key={k} className="px-2 py-1 bg-indigo-50 text-indigo-700 rounded">{k}</span>) : <span className="text-xs text-gray-400">No keywords</span>}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Inline styles / animations */}
      <style>{`
        .loader { border-top-color: transparent; border-right-color: transparent; }
        .animate-pulse { animation: pulse 1.3s cubic-bezier(.4,0,.6,1) infinite; }
        @keyframes pulse { 0% { opacity: .6 } 50% { opacity: 1 } 100% { opacity: .6 } }
        .line-clamp-3 { display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
      `}</style>
    </div>
  );
}
