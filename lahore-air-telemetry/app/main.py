# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.routers import reports, telemetry, zones

app = FastAPI(
    title="LahorePulse API",
    description="Air Quality and Hazard Telemetry Engine for Lahore (LexHack 2026)",
    version="1.0.0",
)

# Enable CORS so local frontends can communicate easily
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(zones.router)
app.include_router(telemetry.router)
app.include_router(reports.router)


@app.get("/", tags=["Root"])
def root_health_check():
    return {
        "status": "online",
        "project": "LahorePulse Telemetry Engine",
        "event": "LexHack 2026",
        "docs_url": "/docs",
    }


# Mount static files for the frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add a redirect to the root url so it automatically goes to the dashboard


@app.get("/", tags=["Root"])
def root_redirect():
    return RedirectResponse(url="/static/index.html")
