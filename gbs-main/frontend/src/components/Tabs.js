import "./AnimatedHeader.css";

export default function Tabs({ tabData, activeTab, setActiveTab }) {
  return (
    <div style={{ display: "flex", gap: 8, borderBottom: "1px solid #ccc" }}>
      {tabData.map((t) => (
        <button
          key={t.key}
          onClick={() => setActiveTab(t.key)}
          className={`tab-button ${activeTab === t.key ? 'active' : ''}`}
          style={{
            padding: "8px 12px",
            border: "none",
            borderBottom: activeTab === t.key ? "2px solid #1976d2" : "2px solid transparent",
            background: "transparent",
            cursor: "pointer",
            fontWeight: activeTab === t.key ? 700 : 400,
          }}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}


