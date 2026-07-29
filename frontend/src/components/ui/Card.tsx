import React from "react";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  onClick?: () => void;
  hoverEffect?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = "",
  style = {},
  onClick,
  hoverEffect = true,
}) => {
  return (
    <div
      onClick={onClick}
      style={{
        backgroundColor: "#11131E",
        borderColor: "rgba(255, 255, 255, 0.05)",
        borderWidth: "1px",
        borderStyle: "solid",
        borderRadius: "22px",
        padding: "24px",
        backdropFilter: "blur(16px)",
        boxShadow: "0 0 40px rgba(123, 62, 255, 0.08)",
        transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        cursor: onClick ? "pointer" : "default",
        ...style,
      }}
      className={`kratos-card ${hoverEffect ? "hover:border-[#7B3EFF]/40 hover:shadow-[0_0_40px_rgba(123,62,255,0.2)]" : ""} ${className}`}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<{ children: React.ReactNode; className?: string; style?: React.CSSProperties }> = ({
  children,
  className = "",
  style = {},
}) => (
  <div style={{ marginBottom: "16px", ...style }} className={className}>
    {children}
  </div>
);

export const CardTitle: React.FC<{ children: React.ReactNode; className?: string; style?: React.CSSProperties }> = ({
  children,
  className = "",
  style = {},
}) => (
  <h3
    style={{
      fontSize: "1rem",
      fontWeight: 600,
      color: "#FFFFFF",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      letterSpacing: "0.02em",
      ...style,
    }}
    className={className}
  >
    {children}
  </h3>
);

export const CardDescription: React.FC<{ children: React.ReactNode; className?: string; style?: React.CSSProperties }> = ({
  children,
  className = "",
  style = {},
}) => (
  <p
    style={{
      fontSize: "0.85rem",
      color: "#A3A8B8",
      marginTop: "6px",
      lineHeight: 1.45,
      ...style,
    }}
    className={className}
  >
    {children}
  </p>
);

export const CardContent: React.FC<{ children: React.ReactNode; className?: string; style?: React.CSSProperties }> = ({
  children,
  className = "",
  style = {},
}) => (
  <div style={style} className={className}>
    {children}
  </div>
);

export const CardFooter: React.FC<{ children: React.ReactNode; className?: string; style?: React.CSSProperties }> = ({
  children,
  className = "",
  style = {},
}) => (
  <div
    style={{
      marginTop: "20px",
      paddingTop: "14px",
      borderTop: "1px solid rgba(255, 255, 255, 0.05)",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      ...style,
    }}
    className={className}
  >
    {children}
  </div>
);
