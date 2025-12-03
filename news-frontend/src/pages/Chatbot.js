// src/pages/Chatbot.js
import React, { useState } from "react";

const API_BASE = "http://localhost:8000"; // adjust if your backend runs elsewhere

function Chatbot() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg.text }),
      }); // Standard fetch POST to API[web:27]

      if (!res.ok) {
        throw new Error("Request failed");
      }
      const data = await res.json();
      const botMsg = { role: "bot", text: data.reply };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Error talking to chatbot." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">NewsPulse Chatbot</h1>

      <div className="border rounded p-3 h-80 overflow-y-auto mb-3 bg-white">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`mb-2 ${
              m.role === "user" ? "text-blue-700" : "text-green-700"
            }`}
          >
            <strong>{m.role === "user" ? "You" : "Bot"}:</strong> {m.text}
          </div>
        ))}
        {messages.length === 0 && (
          <p className="text-gray-500">Start the conversation…</p>
        )}
      </div>

      <form onSubmit={sendMessage} className="flex gap-2">
        <input
          className="flex-1 border rounded px-2 py-1"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about news, trends, etc."
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-3 py-1 rounded"
          disabled={loading}
        >
          {loading ? "Thinking..." : "Send"}
        </button>
      </form>
    </div>
  );
}

export default Chatbot;
