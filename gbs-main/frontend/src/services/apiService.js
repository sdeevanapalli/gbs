const BASE = "http://localhost:8000/api";

export async function getTrials() {
  const r = await fetch(`${BASE}/trials`);
  return r.json();
}

export async function getResources() {
  const r = await fetch(`${BASE}/resources`);
  return r.json();
}

export async function createResource(body) {
  const r = await fetch(`${BASE}/resources`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return r.json();
}

export async function allocateResource(trialId, body) {
  const r = await fetch(`${BASE}/trials/${trialId}/resources`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return r.json();
}

export async function updateTrial(trialId, body) {
  const r = await fetch(`${BASE}/trials/${trialId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return r.json();
}

export async function forecastForTrial(trialId) {
  const r = await fetch(`${BASE}/trials/${trialId}/forecast`, { method: "POST" });
  return r.json();
}


