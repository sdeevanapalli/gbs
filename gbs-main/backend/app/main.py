from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from .routers.trials import router as trials_router
from .websocket_manager import manager

app = FastAPI(
    title="Clinical Trials Resource Dashboard",
    description="""
    Advanced resource management dashboard for clinical drug research.
    
    ## Features
    * Dynamic quarterly data processing
    * Resource bottleneck analysis  
    * Predictive forecasting
    * Trial timeline management
    
    ## Business Rules
    * 1 FTE = 650 subjects = 7 hours/day
    * NTSA reduces effective supply by ~20%
    """,
    version="1.0.1",
    contact={
        "name": "Team Stackoverflowers",
        "email": "shriniketh.d@gmail.com",
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)
app.include_router(trials_router)

@app.get("/")
def read_root():
    return {"message": "Clinical Trials Dashboard API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We only broadcast server-initiated messages; still read to keep connection alive
            await websocket.receive_text()
    except Exception:
        manager.disconnect(websocket)