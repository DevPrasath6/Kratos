import React, { useState, useEffect } from "react";
import { Search, X } from "lucide-react";

interface CommandItem {
  id: string;
  title: string;
  category: string;
  icon: React.ReactNode;
  action: () => void;
}

interface CommandProps {
  isOpen: boolean;
  onClose: () => void;
  items: CommandItem[];
}

export const Command: React.FC<CommandProps> = ({ isOpen, onClose, items }) => {
  const [search, setSearch] = useState("");

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        if (isOpen) onClose();
      }
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const filtered = items.filter(
    (item) =>
      item.title.toLowerCase().includes(search.toLowerCase()) ||
      item.category.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 100,
        backgroundColor: "rgba(0,0,0,0.75)",
        backdropFilter: "blur(6px)",
        display: "flex",
        alignItems: "flex-start",
        justifyContent: "center",
        paddingTop: "15vh",
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "560px",
          backgroundColor: "#12161f",
          border: "1px solid #242b3d",
          borderRadius: "12px",
          overflow: "hidden",
          boxShadow: "0 20px 40px rgba(0,0,0,0.6)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Header */}
        <div
          style={{
            padding: "16px",
            borderBottom: "1px solid #1f2430",
            display: "flex",
            alignItems: "center",
            gap: "12px",
          }}
        >
          <Search size={20} color="#94a3b8" />
          <input
            type="text"
            autoFocus
            placeholder="Type a command or search KRATOS..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              flex: 1,
              backgroundColor: "transparent",
              border: "none",
              outline: "none",
              color: "#f8fafc",
              fontSize: "1rem",
            }}
          />
          <button
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              color: "#94a3b8",
              cursor: "pointer",
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Results List */}
        <div style={{ maxHeight: "320px", overflowY: "auto", padding: "8px" }}>
          {filtered.length === 0 ? (
            <div style={{ padding: "20px", textAlign: "center", color: "#64748b", fontSize: "0.9rem" }}>
              No matching commands found.
            </div>
          ) : (
            filtered.map((item) => (
              <div
                key={item.id}
                onClick={() => {
                  item.action();
                  onClose();
                }}
                style={{
                  padding: "10px 14px",
                  borderRadius: "8px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  cursor: "pointer",
                  color: "#e2e8f0",
                  transition: "backgroundColor 0.15s ease",
                }}
                onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#1b212f")}
                onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                  <div style={{ color: "#3b82f6" }}>{item.icon}</div>
                  <div>
                    <div style={{ fontSize: "0.9rem", fontWeight: 500 }}>{item.title}</div>
                    <div style={{ fontSize: "0.75rem", color: "#64748b" }}>{item.category}</div>
                  </div>
                </div>
                <span style={{ fontSize: "0.7rem", color: "#475569", border: "1px solid #1e2433", padding: "2px 6px", borderRadius: "4px" }}>
                  ↵ Select
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
