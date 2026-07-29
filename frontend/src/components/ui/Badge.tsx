import React from "react";

export type BadgeVariant = "live" | "busy" | "idle" | "offline" | "error" | "info" | "success" | "warning";

interface BadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
  className?: string;
  dot?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = "idle",
  children,
  className = "",
  dot = true,
}) => {
  const getVariantStyles = () => {
    switch (variant) {
      case "live":
      case "success":
        return {
          bg: "bg-emerald-500/10 border-emerald-500/30 text-emerald-400",
          dotBg: "bg-emerald-400 animate-pulse",
        };
      case "busy":
      case "warning":
        return {
          bg: "bg-amber-500/10 border-amber-500/30 text-amber-400",
          dotBg: "bg-amber-400 animate-ping",
        };
      case "error":
        return {
          bg: "bg-rose-500/10 border-rose-500/30 text-rose-400",
          dotBg: "bg-rose-400",
        };
      case "info":
        return {
          bg: "bg-cyan-500/10 border-cyan-500/30 text-cyan-400",
          dotBg: "bg-cyan-400",
        };
      case "offline":
      case "idle":
      default:
        return {
          bg: "bg-slate-800/60 border-slate-700/60 text-slate-400",
          dotBg: "bg-slate-500",
        };
    }
  };

  const style = getVariantStyles();

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border transition-colors ${style.bg} ${className}`}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "6px",
        padding: "2px 10px",
        borderRadius: "9999px",
        fontSize: "0.75rem",
        fontWeight: 500,
        border: "1px solid",
      }}
    >
      {dot && (
        <span
          className={`w-1.5 h-1.5 rounded-full ${style.dotBg}`}
          style={{
            width: "6px",
            height: "6px",
            borderRadius: "50%",
            backgroundColor: "currentColor",
          }}
        />
      )}
      {children}
    </span>
  );
};
