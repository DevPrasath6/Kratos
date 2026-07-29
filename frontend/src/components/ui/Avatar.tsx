import React from "react";

interface AvatarProps {
  name: string;
  role?: string;
  status?: "active" | "busy" | "offline";
  size?: number;
}

export const Avatar: React.FC<AvatarProps> = ({ name, role, status = "active", size = 36 }) => {
  const getInitials = (n: string) => {
    const parts = n.split(" ");
    if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    return n.slice(0, 2).toUpperCase();
  };

  const getStatusColor = () => {
    if (status === "active") return "#10b981";
    if (status === "busy") return "#f59e0b";
    return "#64748b";
  };

  return (
    <div style={{ position: "relative", display: "inline-block" }} title={`${name} (${role || "Responder"})`}>
      <div
        style={{
          width: `${size}px`,
          height: `${size}px`,
          borderRadius: "50%",
          backgroundColor: "#1e2433",
          border: "2px solid #3b82f6",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "#f8fafc",
          fontWeight: 600,
          fontSize: `${size * 0.4}px`,
          boxShadow: "0 2px 8px rgba(0,0,0,0.3)",
        }}
      >
        {getInitials(name)}
      </div>
      {status && (
        <span
          style={{
            position: "absolute",
            bottom: "0",
            right: "0",
            width: `${Math.max(8, size * 0.28)}px`,
            height: `${Math.max(8, size * 0.28)}px`,
            borderRadius: "50%",
            backgroundColor: getStatusColor(),
            border: "2px solid #12161f",
          }}
        />
      )}
    </div>
  );
};

export const AvatarGroup: React.FC<{ items: Array<{ name: string; role?: string }>; max?: number }> = ({
  items,
  max = 4,
}) => {
  const visible = items.slice(0, max);
  const overflow = items.length - max;

  return (
    <div style={{ display: "flex", alignItems: "center" }}>
      {visible.map((item, idx) => (
        <div key={idx} style={{ marginLeft: idx === 0 ? 0 : "-10px", zIndex: visible.length - idx }}>
          <Avatar name={item.name} role={item.role} size={32} />
        </div>
      ))}
      {overflow > 0 && (
        <div
          style={{
            marginLeft: "-10px",
            width: "32px",
            height: "32px",
            borderRadius: "50%",
            backgroundColor: "#242b3d",
            border: "2px solid #12161f",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#94a3b8",
            fontSize: "0.75rem",
            fontWeight: 600,
            zIndex: 0,
          }}
        >
          +{overflow}
        </div>
      )}
    </div>
  );
};
