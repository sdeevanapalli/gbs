import { Bar, BarChart, CartesianGrid, Legend, Tooltip, XAxis, YAxis } from "recharts";
import "./AnimatedHeader.css";

export default function InsightMonitor({ resources, reduceMotion = false }) {
  const data = resources.map((r) => ({
    name: r.skill_type,
    total: r.total_units,
    available: r.available_units,
    allocated: Math.max(0, (r.total_units || 0) - (r.available_units || 0)),
  }));

  return (
    <div className="chart-container">
      <h3>Live Resource Utilization</h3>
      <BarChart width={800} height={300} data={data} barCategoryGap={8}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip animationEasing="ease-out" />
        <Legend />
        <Bar dataKey="allocated" fill="#8884d8" isAnimationActive={!reduceMotion} animationDuration={400} animationEasing="ease-out" />
        <Bar dataKey="available" fill="#82ca9d" isAnimationActive={!reduceMotion} animationDuration={400} animationEasing="ease-out" />
      </BarChart>
    </div>
  );
}


