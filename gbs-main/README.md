# Clinical Trials Resource Dashboard

Full-stack, real-time, and predictive dashboard for clinical trial resource management.

- **Backend:** FastAPI (Python, SQLAlchemy, WebSockets, scikit-learn)
- **Frontend:** React + Vite (Recharts, WebSocket client)

---

## Prerequisites

- Python 3.11+
- Node.js 18+ and pnpm (or npm/yarn)
  - Install pnpm: `npm i -g pnpm`

Ports used (defaults):
- Backend API/WebSocket: `http://localhost:8000` (`/ws/dashboard`)
- Frontend Dev: `http://localhost:5173`

---

## 1) Backend: Setup and Run

From project root:

```bash
cd backend
python -m venv .venv
.venv\\Scripts\\activate  # Windows PowerShell
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# Run FastAPI (reload for dev)
uvicorn app.main:app --reload
```

Notes:
- Uses SQLite by default (a `clinical_trials.db` file will be created automatically in the backend working directory).
- CORS is enabled for `http://localhost:5173`.

Key endpoints (all prefixed with `/api`):
- Trials CRUD: `POST /trials`, `GET /trials`, `GET /trials/{id}`, `PUT /trials/{id}`
- Resources: `GET /resources`, `POST /resources`
- Allocation: `POST /trials/{trial_id}/resources` (updates resource availability and broadcasts via WebSocket)
- Forecast (Phase 2 → Phase 3): `POST /trials/{trial_id}/forecast`
- User quotas (per-user utilization limits): `POST /user-quotas`, `GET /user-quotas`
- WebSocket: `ws://localhost:8000/ws/dashboard`

Business rules enforced:
- Milestones automatically created on status changes: `APPROVED`, `FPFV_REACHED`, `DBL`.
- On `DBL`: all trial allocations are released back to resources and new allocations are blocked.
- Allocation validations: positive units, resource availability, per-user quotas within optional time windows and optional per-trial scope.

Quick cURL examples:

```bash
# Create a resource
curl -X POST http://localhost:8000/api/resources \
  -H "Content-Type: application/json" \
  -d '{"skill_type":"Biostatistician","total_units":10,"available_units":10}'

# Create a trial
curl -X POST http://localhost:8000/api/trials \
  -H "Content-Type: application/json" \
  -d '{"name":"TRIAL-001","sponsor":"ACME","phase":"PHASE_2","status":"PLANNING"}'

# Allocate resource to trial (replace IDs accordingly)
curl -X POST http://localhost:8000/api/trials/1/resources \
  -H "Content-Type: application/json" \
  -d '{"trial_id":1,"resource_id":1,"allocated_units":3,"user_name":"alice"}'

# Forecast for next 4 quarters (only for Phase 2 trials)
curl -X POST http://localhost:8000/api/trials/1/forecast
```

---

## 2) Frontend: Setup and Run

From project root:

```bash
cd frontend
pnpm install
pnpm dev
```

Open `http://localhost:5173` in your browser.

What you should see/do:
- The Dashboard with tabs: Insight Monitor, Trial Tracker, Foresight Forecaster, Live Input.
- Click “+ New Input Tab” to open multiple Live Input forms for concurrent data entry.
- Use Live Input to create resources, allocate units (with optional team/user), and update trial status.
- Toggle “Minimal Motion” to disable animations (also honors system `prefers-reduced-motion`).
- Insight updates live on allocations; Trial Tracker shows milestones; Foresight Forecaster generates Phase 3 demand projections.

---

## 3) Troubleshooting

- Backend not reachable / CORS errors:
  - Ensure backend is on `http://localhost:8000` and frontend on `http://localhost:5173`.
  - Restart both servers after port changes.
- WebSocket not connecting:
  - Confirm backend logs show `Uvicorn running on http://127.0.0.1:8000` and no firewall blocks.
  - The client connects to `ws://localhost:8000/ws/dashboard`.
- Reset local data:
  - Stop backend, delete `clinical_trials.db`, then restart backend to recreate tables.
- Quota rejections:
  - Check existing allocations for the user and quota windows; adjust `max_units`, `trial_id`, `start_date`, `end_date` accordingly.

---

## 4) Tech Notes

- Database default is SQLite for local/demo. Swap to Postgres by changing the SQLAlchemy engine in `backend/app/routers/trials.py` and adding the proper DSN/driver.
- Forecasting uses a lightweight Linear Regression retrained on demand with mock historicals (hackathon-ready).
- Animations are CSS-based and lightweight; charts use Recharts easing. A Minimal Motion toggle is provided for accessibility and performance.

---

### Developers

- [Shriniketh Deevanapalli](https://github.com/sdeevanapalli)
- [Kushagra Singh](https://github.com/LuciferK47)
- [Dandu Asrith](https://github.com/asrith-306)
- [Shambhavi Rani](https://github.com/shambhavi233)
- [Venkata Sai Sohan Krishnamsetty](https://github.com/Kvs-sohan)