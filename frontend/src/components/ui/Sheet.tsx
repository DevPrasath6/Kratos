import React from "react";
import { X } from "lucide-react";

interface SheetProps {
  isOpen: boolean;
  onClose: () => void;
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  children: React.ReactNode;
}

export const Sheet: React.FC<SheetProps> = ({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
}) => {
  if (!isOpen) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 50,
        display: "flex",
        justifyContent: "flex-end",
        backgroundColor: "rgba(0, 0, 0, 0.7)",
        backdropFilter: "blur(4px)",
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "600px",
          height: "100%",
          backgroundColor: "#0d1117",
          borderLeft: "1px solid #242b3d",
          boxShadow: "-10px 0 30px rgba(0,0,0,0.5)",
          display: "flex",
          flexDirection: "column",
          overflowY: "auto",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          style={{
            padding: "20px",
            borderBottom: "1px solid #1f2430",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            backgroundColor: "#12161f",
          }}
        >
          <div>
            <h2 style={{ fontSize: "1.25rem", color: "#f8fafc", fontWeight: 600 }}>{title}</h2>
            {subtitle && <p style={{ fontSize: "0.85rem", color: "#94a3b8", marginTop: "4px" }}>{subtitle}</p>}
          </div>
          <button
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              color: "#94a3b8",
              cursor: "pointer",
              padding: "6px",
              borderRadius: "6px",
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Content Body */}
        <div style={{ padding: "20px", flex: 1 }}>{children}</div>
      </div>
    </div>
  );
};
