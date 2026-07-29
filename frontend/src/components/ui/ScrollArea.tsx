import React from "react";

interface ScrollAreaProps {
  maxHeight?: string | number;
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}

export const ScrollArea: React.FC<ScrollAreaProps> = ({
  maxHeight = "300px",
  children,
  className = "",
  style = {},
}) => {
  return (
    <div
      style={{
        maxHeight,
        overflowY: "auto",
        overflowX: "hidden",
        paddingRight: "6px",
        ...style,
      }}
      className={className}
    >
      {children}
    </div>
  );
};
