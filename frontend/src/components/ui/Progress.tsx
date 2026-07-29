import React from "react";

interface ProgressProps {
  value: number; // 0 to 100
  color?: string;
  height?: number;
  className?: string;
}

export const Progress: React.FC<ProgressProps> = ({
  value,
  color = "#7B3EFF",
  height = 6,
  className = "",
}) => {
  const percentage = Math.min(100, Math.max(0, value));

  return (
    <div
      style={{
        width: "100%",
        height: `${height}px`,
        backgroundColor: "#0D1018",
        borderRadius: `${height / 2}px`,
        overflow: "hidden",
        border: "1px solid rgba(255, 255, 255, 0.05)",
      }}
      className={className}
    >
      <div
        style={{
          width: `${percentage}%`,
          height: "100%",
          backgroundColor: color,
          borderRadius: `${height / 2}px`,
          boxShadow: `0 0 12px ${color}`,
          transition: "width 0.5s cubic-bezier(0.4, 0, 0.2, 1)",
        }}
      />
    </div>
  );
};
