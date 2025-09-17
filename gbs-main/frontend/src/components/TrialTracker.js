import "./AnimatedHeader.css";

export default function TrialTracker({ trials }) {
  return (
    <div>
      <h3>Trials Timeline</h3>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {trials.map((t) => (
          <li key={t.id} className="trial-card" style={{ marginBottom: 12, padding: 12, border: "1px solid #ddd", borderRadius: 8 }}>
            <div style={{ fontWeight: 700 }}>{t.name} • {t.sponsor}</div>
            <div>Phase: {t.phase} | Status: {t.status}</div>
            <div style={{ marginTop: 8, display: "flex", gap: 8, flexWrap: "wrap" }}>
              {(t.milestones || []).map((m) => (
                <span key={m.id} className="milestone-badge" style={{ padding: "4px 8px", borderRadius: 999, background: "#eef2ff", border: "1px solid #c7d2fe" }}>
                  {m.milestone_name} — {new Date(m.date_achieved).toLocaleString()}
                </span>
              ))}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}


