import React from "react";

export interface TabItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  badge?: string | number;
}

interface TabsProps {
  tabs: TabItem[];
  activeTab: string;
  onChange: (id: string) => void;
}

export const Tabs: React.FC<TabsProps> = ({ tabs, activeTab, onChange }) => {
  return (
    <nav style={{ display: "flex", alignItems: "center", gap: "32px", position: "relative" }}>
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            style={{
              background: "none",
              border: "none",
              padding: "12px 0",
              fontSize: "0.9rem",
              fontWeight: isActive ? 600 : 500,
              color: isActive ? "#FFFFFF" : "#A3A8B8",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              position: "relative",
              transition: "color 300ms ease",
              outline: "none",
            }}
            onMouseEnter={(e) => {
              if (!isActive) e.currentTarget.style.color = "#FFFFFF";
            }}
            onMouseLeave={(e) => {
              if (!isActive) e.currentTarget.style.color = "#A3A8B8";
            }}
          >
            {tab.icon && (
              <span style={{ color: isActive ? "#7B3EFF" : "inherit", transition: "color 300ms ease" }}>
                {tab.icon}
              </span>
            )}
            <span>{tab.label}</span>
            {tab.badge !== undefined && (
              <span
                style={{
                  fontSize: "0.7rem",
                  padding: "1px 6px",
                  borderRadius: "10px",
                  backgroundColor: isActive ? "#7B3EFF" : "rgba(255,255,255,0.08)",
                  color: "#FFFFFF",
                  fontWeight: 600,
                }}
              >
                {tab.badge}
              </span>
            )}

            {/* Glowing Electric Cyan Underline Indicator */}
            {isActive && (
              <span
                style={{
                  position: "absolute",
                  bottom: "-2px",
                  left: 0,
                  right: 0,
                  height: "2px",
                  backgroundColor: "#00F2FE",
                  boxShadow: "0 0 12px #00F2FE",
                  borderRadius: "2px",
                }}
              />
            )}
          </button>
        );
      })}
    </nav>
  );
};
