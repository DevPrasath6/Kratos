import React, { useState } from "react";
import { Bot, X, Send, Cpu } from "lucide-react";

export const NemotronChatWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [inputPrompt, setInputPrompt] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [messages, setMessages] = useState<Array<{ sender: "user" | "bot"; text: string; time: string }>>([
    {
      sender: "bot",
      text: "NVIDIA Nemotron 120B NIM Assistant ready.\nAsk any tactical disaster query regarding route optimization, shelter allocations, or infrastructure damage.",
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);

  const handleSend = async () => {
    if (!inputPrompt.trim() || isThinking) return;
    const nowStr = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    const userMsg = inputPrompt.trim();
    setMessages((prev) => [...prev, { sender: "user", text: userMsg, time: nowStr }]);
    setInputPrompt("");
    setIsThinking(true);

    try {
      const resp = await fetch("http://localhost:8000/api/agents/report_generation/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ use_sample: true, prompt: userMsg }),
      });
      const data = await resp.json();
      const botReply = data?.result?.summary || data?.result?.llm_response || "Nemotron LLM analysis completed successfully.";
      setMessages((prev) => [...prev, { sender: "bot", text: botReply, time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }]);
    } catch {
      setMessages((prev) => [...prev, { sender: "bot", text: "Nemotron AI service endpoint unreachable.", time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }]);
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: "fixed",
          bottom: "24px",
          right: "24px",
          zIndex: 999,
          backgroundColor: "#0D1117",
          border: "1px solid #38BDF8",
          color: "#38BDF8",
          width: "52px",
          height: "52px",
          borderRadius: "50%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: "0 0 20px rgba(56, 189, 248, 0.35)",
          cursor: "pointer",
          transition: "transform 0.2s ease",
        }}
        title="Open Nemotron AI Chatbot"
      >
        {isOpen ? <X size={22} /> : <Bot size={24} />}
      </button>

      {/* Floating Chat Modal Box */}
      {isOpen && (
        <div
          style={{
            position: "fixed",
            bottom: "86px",
            right: "24px",
            width: "360px",
            height: "480px",
            backgroundColor: "#0D1117",
            border: "1px solid #21262D",
            borderRadius: "12px",
            boxShadow: "0 10px 40px rgba(0, 0, 0, 0.8)",
            zIndex: 999,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          {/* Header */}
          <div style={{ padding: "14px 16px", backgroundColor: "#161B22", borderBottom: "1px solid #21262D", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <Cpu size={18} color="#38BDF8" />
              <div>
                <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "#F0F6FC", fontFamily: "var(--mono-font)" }}>NEMOTRON AI ASSISTANT</div>
                <div style={{ fontSize: "0.65rem", color: "#10B981", fontFamily: "var(--mono-font)" }}>NVIDIA 120B NIM ONLINE</div>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} style={{ backgroundColor: "transparent", border: "none", color: "#8B949E", cursor: "pointer" }}>
              <X size={16} />
            </button>
          </div>

          {/* Messages Container */}
          <div style={{ flex: 1, overflowY: "auto", padding: "14px", display: "flex", flexDirection: "column", gap: "10px" }}>
            {messages.map((m, idx) => (
              <div
                key={idx}
                style={{
                  alignSelf: m.sender === "user" ? "flex-end" : "flex-start",
                  maxWidth: "85%",
                  backgroundColor: "#161B22",
                  border: `1px solid ${m.sender === "user" ? "#38BDF8" : "#21262D"}`,
                  borderRadius: "8px",
                  padding: "8px 12px",
                }}
              >
                <div style={{ fontSize: "0.78rem", color: "#F0F6FC", whiteSpace: "pre-line", lineHeight: 1.4 }}>{m.text}</div>
                <span style={{ fontSize: "0.6rem", color: "#484F58", display: "block", marginTop: "4px", textAlign: "right", fontFamily: "var(--mono-font)" }}>{m.time}</span>
              </div>
            ))}
            {isThinking && (
              <div style={{ fontSize: "0.72rem", color: "#38BDF8", fontFamily: "var(--mono-font)" }}>
                Querying Nemotron NIM model...
              </div>
            )}
          </div>

          {/* Input Footer */}
          <div style={{ padding: "10px", backgroundColor: "#161B22", borderTop: "1px solid #21262D", display: "flex", gap: "8px" }}>
            <input
              type="text"
              value={inputPrompt}
              onChange={(e) => setInputPrompt(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Ask Nemotron disaster query..."
              style={{
                flex: 1,
                backgroundColor: "#0D1117",
                border: "1px solid #21262D",
                borderRadius: "6px",
                padding: "8px 10px",
                color: "#F0F6FC",
                fontSize: "0.75rem",
                fontFamily: "var(--mono-font)",
                outline: "none",
              }}
            />
            <button
              onClick={handleSend}
              disabled={isThinking}
              style={{
                backgroundColor: "#38BDF8",
                border: "none",
                borderRadius: "6px",
                padding: "8px 12px",
                color: "#090C10",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Send size={14} />
            </button>
          </div>
        </div>
      )}
    </>
  );
};
