from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

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

@app.get("/")
def read_root():
    return {"message": "Clinical Trials Dashboard API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}