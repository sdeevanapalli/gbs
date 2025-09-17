import { useState } from "react";
import { createResource, updateTrial, allocateResource } from "../services/apiService";
import "./AnimatedHeader.css";

export default function LiveInput({ trials, resources }) {
  const [resForm, setResForm] = useState({ skill_type: "", total_units: 10, available_units: 10 });
  const [allocForm, setAllocForm] = useState({ trial_id: "", resource_id: "", allocated_units: 1 });
  const [statusForm, setStatusForm] = useState({ trial_id: "", status: "APPROVED" });
  const [userName, setUserName] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const onCreateResource = async (e) => {
    e.preventDefault();
    if (!resForm.skill_type) return;
    const res = await createResource({
      skill_type: resForm.skill_type,
      total_units: Number(resForm.total_units),
      available_units: Number(resForm.available_units),
    });
    setSuccess(`Resource created: ${res.skill_type}`);
    setTimeout(() => setSuccess(""), 2000);
  };

  const onAllocate = async (e) => {
    e.preventDefault();
    if (!allocForm.trial_id || !allocForm.resource_id) return;
    setError("");
    try {
      await allocateResource(Number(allocForm.trial_id), {
        trial_id: Number(allocForm.trial_id),
        resource_id: Number(allocForm.resource_id),
        allocated_units: Number(allocForm.allocated_units),
        user_name: userName || null,
      });
      setSuccess("Allocation succeeded");
      setTimeout(() => setSuccess(""), 1500);
    } catch (e) {
      setError("Allocation failed. Check quotas and availability.");
    }
  };

  const onUpdateStatus = async (e) => {
    e.preventDefault();
    if (!statusForm.trial_id) return;
    await updateTrial(Number(statusForm.trial_id), { status: statusForm.status });
  };

  return (
    <div style={{ display: "grid", gap: 16, gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))" }}>
      <form onSubmit={onCreateResource} style={{ border: "1px solid #ddd", borderRadius: 8, padding: 12 }}>
        <h4>Create Resource</h4>
        <input
          placeholder="Skill type"
          value={resForm.skill_type}
          onChange={(e) => setResForm({ ...resForm, skill_type: e.target.value })}
          className="form-input"
          style={{ width: "100%", marginBottom: 8 }}
        />
        <input
          type="number"
          placeholder="Total units"
          value={resForm.total_units}
          onChange={(e) => setResForm({ ...resForm, total_units: e.target.value })}
          className="form-input"
          style={{ width: "100%", marginBottom: 8 }}
        />
        <input
          type="number"
          placeholder="Available units"
          value={resForm.available_units}
          onChange={(e) => setResForm({ ...resForm, available_units: e.target.value })}
          className="form-input"
          style={{ width: "100%", marginBottom: 8 }}
        />
        <button type="submit" className="btn-primary">Create</button>
      </form>

      <form onSubmit={onAllocate} style={{ border: "1px solid #ddd", borderRadius: 8, padding: 12 }}>
        <h4>Allocate Resource</h4>
        {success && <div className="success-message">{success}</div>}
        {error && <div className="error-message">{error}</div>}
        <select
          value={allocForm.trial_id}
          onChange={(e) => setAllocForm({ ...allocForm, trial_id: e.target.value })}
          style={{ width: "100%", marginBottom: 8 }}
        >
          <option value="">Select trial</option>
          {(trials || []).map((t) => (
            <option key={t.id} value={t.id}>{t.name}</option>
          ))}
        </select>
        <select
          value={allocForm.resource_id}
          onChange={(e) => setAllocForm({ ...allocForm, resource_id: e.target.value })}
          style={{ width: "100%", marginBottom: 8 }}
        >
          <option value="">Select resource</option>
          {(resources || []).map((r) => (
            <option key={r.id} value={r.id}>{r.skill_type}</option>
          ))}
        </select>
        <input
          placeholder="User name (optional)"
          value={userName}
          onChange={(e) => setUserName(e.target.value)}
          className="form-input"
          style={{ width: "100%", marginBottom: 8 }}
        />
        <input
          type="number"
          placeholder="Units"
          value={allocForm.allocated_units}
          onChange={(e) => setAllocForm({ ...allocForm, allocated_units: e.target.value })}
          className="form-input"
          style={{ width: "100%", marginBottom: 8 }}
        />
        <button type="submit" className="btn-primary">Allocate</button>
      </form>

      <form onSubmit={onUpdateStatus} style={{ border: "1px solid #ddd", borderRadius: 8, padding: 12 }}>
        <h4>Update Trial Status</h4>
        <select
          value={statusForm.trial_id}
          onChange={(e) => setStatusForm({ ...statusForm, trial_id: e.target.value })}
          style={{ width: "100%", marginBottom: 8 }}
        >
          <option value="">Select trial</option>
          {(trials || []).map((t) => (
            <option key={t.id} value={t.id}>{t.name}</option>
          ))}
        </select>
        <select
          value={statusForm.status}
          onChange={(e) => setStatusForm({ ...statusForm, status: e.target.value })}
          style={{ width: "100%", marginBottom: 8 }}
        >
          {[
            "PLANNING",
            "APPROVED",
            "RECRUITING",
            "FPFV_REACHED",
            "ACTIVE",
            "DBL",
            "COMPLETED",
          ].map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <button type="submit" className="btn-primary">Update</button>
      </form>
    </div>
  );
}


