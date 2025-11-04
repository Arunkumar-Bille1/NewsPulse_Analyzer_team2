import React, { useState } from "react";
import axios from "axios";

function RawAnalysis() {
  const [input, setInput] = useState("");
  const [sentiment, setSentiment] = useState(null);
  const [entities, setEntities] = useState([]);
  const [error, setError] = useState("");

  const handleAnalyze = async () => {
    setError("");
    setSentiment(null);
    setEntities([]);
    try {
      // Sentiment
      const sentResp = await axios.get("http://127.0.0.1:8000/sentiment", {
        params: { text: input }
      });
      setSentiment(sentResp.data.sentiment);

      // NER
      const nerResp = await axios.get("http://127.0.0.1:8000/ner", {
        params: { text: input }
      });
      setEntities(nerResp.data.entities || []);
    } catch (e) {
      setError("Analysis failed. Please try again.");
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded shadow">
      <h1 className="text-2xl font-bold mb-4">Raw Text Analysis</h1>
      <textarea
        className="w-full p-2 border border-gray-300 rounded mb-4"
        rows={5}
        value={input}
        onChange={e => setInput(e.target.value)}
        placeholder="Paste or type your text here..."
      />
      <button
        onClick={handleAnalyze}
        className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 transition disabled:opacity-50"
        disabled={!input.trim()}
      >
        Analyze
      </button>
      {error && <div className="mt-4 text-red-500">{error}</div>}

      {/* Sentiment */}
      {sentiment && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-2">Sentiment Analysis</h2>
          {sentiment && sentiment.all_scores && (
  <div className="mb-2">
    {Object.entries(sentiment.all_scores).map(([label, score]) => (
      <div key={label} className="flex items-center gap-2 mb-1">
        <span className="capitalize w-20">{label.toLowerCase()}:</span>
        <div className="h-2 bg-indigo-300 rounded" style={{ width: `${Math.round(score * 100)}%`, minWidth: 20 }} />
        <span className="ml-2 text-sm">{Math.round(score * 100)}%</span>
      </div>
    ))}
    {/* Final label */}
    <div className="mt-2">
      <span className="font-bold">{sentiment.label}</span>
      <span className="ml-2 text-gray-700">
        (Confidence: {Math.round(sentiment.confidence * 100)}%)
      </span>
    </div>
  </div>
)}

        </div>
      )}

      {/* Entities */}
      {entities && (
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
      )}
    </div>
  );
}

export default RawAnalysis;
