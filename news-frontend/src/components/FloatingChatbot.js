import React, { useState } from "react";

const FloatingChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);     // open/closed
  const [isMinimized, setIsMinimized] = useState(false); // minimized state
  const [messages, setMessages] = useState([]);    // chat history for current session
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleToggleOpen = () => {
    // when opening from icon, keep previous minimized history
    setIsOpen(true);
    setIsMinimized(false);
  };

  const handleClose = () => {
    // close and clear session
    setIsOpen(false);
    setIsMinimized(false);
    setMessages([]);
    setInput("");
  };

  const handleMinimize = () => {
    // hide panel but keep messages in state
    setIsMinimized(true);
    setIsOpen(false);
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg.text }),
      }); // Standard fetch POST to chatbot endpoint[web:27][web:56]

      const data = await res.json();
      const botMsg = { role: "bot", text: data.reply || "No reply" };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Error talking to assistant." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating button (always visible on dashboard) */}
      {!isOpen && (
        <button
          onClick={handleToggleOpen}
          style={{
            position: "fixed",
            bottom: "24px",
            right: "24px",
            width: "56px",
            height: "56px",
            borderRadius: "50%",
            backgroundColor: "#4F46E5",
            color: "white",
            border: "none",
            boxShadow: "0 4px 10px rgba(0,0,0,0.2)",
            cursor: "pointer",
            zIndex: 9999,
          }}
        >
          💬
        </button>
      )}

      {/* Chat window overlay */}
      {isOpen && (
        <div
          style={{
            position: "fixed",
            bottom: "90px",
            right: "24px",
            width: "340px",
            height: "480px",
            backgroundColor: "#f9fafb",
            borderRadius: "16px",
            boxShadow: "0 10px 30px rgba(15,23,42,0.3)",
            display: "flex",
            flexDirection: "column",
            zIndex: 10000,
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: "10px 14px",
              borderBottom: "1px solid #e5e7eb",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              background: "#4F46E5",
              color: "white",
              borderTopLeftRadius: "16px",
              borderTopRightRadius: "16px",
            }}
          >
            <div>
              <div style={{ fontWeight: "600", fontSize: "14px" }}>
                TrendVista Assistant
              </div>
              <div style={{ fontSize: "11px", opacity: 0.9 }}>
                Ask about news & trends
              </div>
            </div>
            <div style={{ display: "flex", gap: "6px" }}>
              <button
                onClick={handleMinimize}
                title="Minimize"
                style={{
                  border: "none",
                  background: "rgba(15,23,42,0.15)",
                  color: "white",
                  width: "24px",
                  height: "24px",
                  borderRadius: "999px",
                  cursor: "pointer",
                  fontSize: "14px",
                }}
              >
                _
              </button>
              <button
                onClick={handleClose}
                title="Close"
                style={{
                  border: "none",
                  background: "rgba(15,23,42,0.15)",
                  color: "white",
                  width: "24px",
                  height: "24px",
                  borderRadius: "999px",
                  cursor: "pointer",
                  fontSize: "14px",
                }}
              >
                ×
              </button>
            </div>
          </div>

          {/* Messages area */}
          <div
            style={{
              flex: 1,
              padding: "10px",
              overflowY: "auto",
              background: "#e0f2fe",
            }}
          >
            {messages.length === 0 && (
              <p style={{ fontSize: "12px", color: "#4b5563" }}>
                Ask anything about current news, topics, or your dashboard data.
              </p>
            )}

            {messages.map((m, idx) => (
              <div
                key={idx}
                style={{
                  marginBottom: "8px",
                  display: "flex",
                  justifyContent:
                    m.role === "user" ? "flex-end" : "flex-start",
                }}
              >
                <div
                  style={{
                    maxWidth: "80%",
                    padding: "8px 10px",
                    borderRadius: "12px",
                    fontSize: "12px",
                    backgroundColor:
                      m.role === "user" ? "#4F46E5" : "#ffffff",
                    color: m.role === "user" ? "#ffffff" : "#111827",
                  }}
                >
                  {m.text}
                </div>
              </div>
            ))}

            {loading && (
              <div style={{ fontSize: "12px", color: "#4b5563" }}>
                Assistant is typing…
              </div>
            )}
          </div>

          {/* Input bar */}
          <form
            onSubmit={sendMessage}
            style={{
              borderTop: "1px solid #e5e7eb",
              padding: "8px",
              display: "flex",
              gap: "6px",
              background: "#f9fafb",
              borderBottomLeftRadius: "16px",
              borderBottomRightRadius: "16px",
            }}
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Write message here…"
              style={{
                flex: 1,
                borderRadius: "999px",
                border: "1px solid #d1d5db",
                padding: "6px 10px",
                fontSize: "12px",
              }}
            />
            <button
              type="submit"
              disabled={loading}
              style={{
                width: "34px",
                height: "34px",
                borderRadius: "999px",
                border: "none",
                backgroundColor: "#22c55e",
                color: "white",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "18px",
              }}
            >
              ↑
            </button>
          </form>
        </div>
      )}

      {/* When minimized, small pill with unread icon (optional) */}
      {isMinimized && (
        <button
          onClick={handleToggleOpen}
          style={{
            position: "fixed",
            bottom: "24px",
            right: "24px",
            padding: "10px 14px",
            borderRadius: "999px",
            backgroundColor: "#4F46E5",
            color: "white",
            border: "none",
            boxShadow: "0 4px 10px rgba(0,0,0,0.2)",
            cursor: "pointer",
            zIndex: 9999,
            fontSize: "13px",
            display: "flex",
            alignItems: "center",
            gap: "6px",
          }}
        >
          💬 Assistant
        </button>
      )}
    </>
  );
};

export default FloatingChatbot;
