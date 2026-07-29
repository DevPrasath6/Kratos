import React from "react";

export const Table: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className = "",
}) => (
  <div style={{ width: "100%", overflowX: "auto", borderRadius: "8px", border: "1px solid #1f2430" }}>
    <table
      style={{
        width: "100%",
        borderCollapse: "collapse",
        textAlign: "left",
        fontSize: "0.875rem",
        backgroundColor: "#12161f",
      }}
      className={className}
    >
      {children}
    </table>
  </div>
);

export const TableHeader: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <thead style={{ backgroundColor: "#181d29", borderBottom: "1px solid #242b3d" }}>{children}</thead>
);

export const TableRow: React.FC<{ children: React.ReactNode; onClick?: () => void }> = ({
  children,
  onClick,
}) => (
  <tr
    onClick={onClick}
    style={{
      borderBottom: "1px solid #1e2433",
      cursor: onClick ? "pointer" : "default",
      transition: "background-color 0.15s ease",
    }}
  >
    {children}
  </tr>
);

export const TableHead: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({
  children,
  style,
}) => (
  <th
    style={{
      padding: "12px 16px",
      fontWeight: 600,
      color: "#94a3b8",
      fontSize: "0.75rem",
      textTransform: "uppercase",
      letterSpacing: "0.05em",
      ...style,
    }}
  >
    {children}
  </th>
);

export const TableCell: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({
  children,
  style,
}) => (
  <td style={{ padding: "12px 16px", color: "#e2e8f0", ...style }}>{children}</td>
);
