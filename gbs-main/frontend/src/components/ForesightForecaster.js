import { useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, Tooltip, XAxis, YAxis } from "recharts";
import "./AnimatedHeader.css";
import { forecastForTrial } from "../services/apiService";

export default function ForesightForecaster({ trials, forecastData, setForecastData, reduceMotion = false }) {
  const phase2Trials = (trials || []).filter((t) => t.phase === "PHASE_2");
  const [selectedId, setSelectedId] = useState(phase2Trials[0]?.id || null);
  const data = forecastData[selectedId] || [];
  const [loading, setLoading] = useState(false);

  const onForecast = async () => {
    if (!selectedId) return;
    setLoading(true);
    try {
      const res = await forecastForTrial(selectedId);
      setForecastData((prev) => ({ ...prev, [selectedId]: res.forecasts }));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h3>Phase 2 → Phase 3 Forecast</h3>
      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <select value={selectedId || ""} onChange={(e) => setSelectedId(Number(e.target.value))}>
          {phase2Trials.map((t) => (
            <option key={t.id} value={t.id}>{t.name}</option>
          ))}
        </select>
        <button onClick={onForecast}>Generate Forecast</button>
      </div>

      <div style={{ marginTop: 16 }} className={`chart-container ${loading ? 'chart-loading' : ''}`}>
        <button onClick={onForecast} disabled={loading} className="btn-primary">
          {loading ? <span className="loading-spinner" /> : null}
          {loading ? " Generating..." : "Regenerate Forecast"}
        </button>
      </div>

      {data.length > 0 && (
        <div style={{ marginTop: 16 }} className={`chart-container ${loading ? 'chart-loading' : ''}`}>
          <BarChart width={800} height={320} data={data} barCategoryGap={10}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={(d) => `${d.year}-Q${d.quarter}`} />
            <YAxis />
            <Tooltip animationEasing="ease-out" />
            <Legend />
            <Bar dataKey="units_demanded" name="Units" fill="#8884d8" isAnimationActive={!reduceMotion} animationDuration={450} animationEasing="ease-out" />
          </BarChart>
        </div>
      )}
    </div>
  );
}


