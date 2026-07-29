import React from "react";

interface SeparatorProps {
  orientation?: "horizontal" | "vertical";
  className?: string;
  style?: React.CSSProperties;
}

export const Separator: React.FC<SeparatorProps> = ({
  orientation = "horizontal",
  className = "",
  style = {},
}) => {
  if (orientation === "vertical") {
    return (
      <div
        style={{
          width: "1px",
          height: "100%",
          backgroundColor: "rgba(255, 255, 255, 0.08)",
          ...style,
        }}
        className={className}
      />
    );
  }

  return (
    <div
      style={{
        width: "100%",
        height: "1px",
        backgroundColor: "rgba(255, 255, 255, 0.08)",
        margin: "12px 0",
        ...style,
      }}
      className={className}
    />
  );
};
