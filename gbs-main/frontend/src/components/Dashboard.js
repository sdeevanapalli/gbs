import { useEffect, useMemo, useState } from "react";
import { getTrials, getResources, allocateResource, forecastForTrial } from "../services/apiService";
import Tabs from "./Tabs";
import InsightMonitor from "./InsightMonitor";
import TrialTracker from "./TrialTracker";
import ForesightForecaster from "./ForesightForecaster";
import LiveInput from "./LiveInput";
import "./AnimatedHeader.css";

export default function Dashboard() {
  const [trials, setTrials] = useState([]);
  const [resources, setResources] = useState([]);
  const [forecastData, setForecastData] = useState({});
  const [socket, setSocket] = useState(null);
  const [reduceMotion, setReduceMotion] = useState(() => window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  useEffect(() => {
    (async () => {
      const [t, r] = await Promise.all([getTrials(), getResources()]);
      setTrials(t);
      setResources(r);
    })();
  }, []);

  useEffect(() => {
    const s = new WebSocket("ws://localhost:8000/ws/dashboard");
    s.onopen = () => console.log("WebSocket connection established");
    s.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "allocation_created") {
        setResources((prev) => prev.map((res) => (res.id === data.resource.id ? data.resource : res)));
      }
      if (data.type === "resources_update") {
        setResources(data.resources);
      }
    };
    s.onclose = () => console.log("WebSocket connection closed");
    setSocket(s);
    return () => s.close();
  }, []);

  const [dynamicTabs, setDynamicTabs] = useState([]);
  const tabData = useMemo(
    () => [
      { key: "insight", label: "Insight Monitor" },
      { key: "tracker", label: "Trial Tracker" },
      { key: "foresight", label: "Foresight Forecaster" },
      { key: "live", label: "Live Input" },
      ...dynamicTabs,
    ],
    [dynamicTabs]
  );
  const [activeTab, setActiveTab] = useState("insight");

  const addNewInputTab = () => {
    const id = `live-${Date.now()}`;
    setDynamicTabs((prev) => [...prev, { key: id, label: `Live Input ${prev.length + 1}`, type: "live" }]);
    setActiveTab(id);
  };

  return (
    <div style={{ padding: 16 }} className={reduceMotion ? 'reduce-motion' : ''}>
      <div className="header">
        <div className="header-title">Clinical Trials Resource Dashboard</div>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <Tabs tabData={tabData} activeTab={activeTab} setActiveTab={setActiveTab} />
        <button className="pulse-btn" onClick={addNewInputTab}>+ New Input Tab</button>
        <label style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6 }}>
          <input type="checkbox" checked={reduceMotion} onChange={(e) => setReduceMotion(e.target.checked)} />
          Minimal Motion
        </label>
      </div>
      <div style={{ marginTop: 16 }} className="panel">
        {activeTab === "insight" && <InsightMonitor resources={resources} trials={trials} reduceMotion={reduceMotion} />}
        {activeTab === "tracker" && <TrialTracker trials={trials} />}
        {activeTab === "foresight" && (
          <ForesightForecaster trials={trials} forecastData={forecastData} setForecastData={setForecastData} reduceMotion={reduceMotion} />
        )}
        {(activeTab === "live" || dynamicTabs.some((t) => t.key === activeTab && t.type === "live")) && (
          <LiveInput trials={trials} resources={resources} />
        )}
      </div>
    </div>
  );
}


