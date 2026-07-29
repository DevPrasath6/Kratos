import React, { useState } from "react";

interface TooltipProps {
  content: React.ReactNode;
  children: React.ReactNode;
  position?: "top" | "bottom" | "left" | "right";
}

export const Tooltip: React.FC<TooltipProps> = ({ content, children }) => {
  const [show, setShow] = useState(false);

  return (
    <div
      style={{ position: "relative", display: "inline-block" }}
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
    >
      {children}
      {show && (
        <div
          style={{
            position: "absolute",
            bottom: "100%",
            left: "50%",
            transform: "translateX(-50%)",
            marginBottom: "8px",
            padding: "6px 10px",
            backgroundColor: "#0d1117",
            border: "1px solid #30363d",
            borderRadius: "6px",
            color: "#e2e8f0",
            fontSize: "0.75rem",
            whiteSpace: "nowrap",
            zIndex: 40,
            boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
            pointerEvents: "none",
          }}
        >
          {content}
        </div>
      )}
    </div>
  );
};

export const Popover: React.FC<{ content: React.ReactNode; children: React.ReactNode }> = ({
  content,
  children,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div style={{ position: "relative", display: "inline-block" }}>
      <div onClick={() => setIsOpen(!isOpen)}>{children}</div>
      {isOpen && (
        <div
          style={{
            position: "absolute",
            top: "100%",
            right: 0,
            marginTop: "8px",
            width: "280px",
            backgroundColor: "#12161f",
            border: "1px solid #242b3d",
            borderRadius: "8px",
            padding: "16px",
            boxShadow: "0 10px 30px rgba(0,0,0,0.6)",
            zIndex: 50,
          }}
        >
          {content}
        </div>
      )}
    </div>
  );
};
