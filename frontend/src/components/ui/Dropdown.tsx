import React, { useState } from "react";
import { ChevronDown } from "lucide-react";

export interface DropdownItem {
  id: string;
  label: string;
  action: () => void;
}

interface DropdownProps {
  label: string;
  items: DropdownItem[];
}

export const Dropdown: React.FC<DropdownProps> = ({ label, items }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div style={{ position: "relative", display: "inline-block" }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          backgroundColor: "#11131E",
          border: "1px solid rgba(255, 255, 255, 0.08)",
          color: "#FFFFFF",
          padding: "8px 14px",
          borderRadius: "10px",
          fontSize: "0.85rem",
          fontWeight: 600,
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          gap: "8px",
          transition: "all 0.2s ease",
        }}
      >
        <span>{label}</span>
        <ChevronDown size={14} color="#A3A8B8" />
      </button>

      {isOpen && (
        <div
          style={{
            position: "absolute",
            top: "100%",
            right: 0,
            marginTop: "6px",
            width: "180px",
            backgroundColor: "#0D1018",
            border: "1px solid rgba(123, 62, 255, 0.3)",
            borderRadius: "12px",
            padding: "6px",
            boxShadow: "0 10px 30px rgba(0, 0, 0, 0.8)",
            zIndex: 50,
          }}
        >
          {items.map((item) => (
            <div
              key={item.id}
              onClick={() => {
                item.action();
                setIsOpen(false);
              }}
              style={{
                padding: "8px 12px",
                fontSize: "0.85rem",
                color: "#FFFFFF",
                borderRadius: "8px",
                cursor: "pointer",
                transition: "background-color 0.15s ease",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "rgba(123, 62, 255, 0.2)")}
              onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
            >
              {item.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
