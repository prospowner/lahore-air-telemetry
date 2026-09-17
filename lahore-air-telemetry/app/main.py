# app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.notifications import send_discord_alert
from app.routers import reports, telemetry, zones
from app.services.ingest import fetch_and_store_owm_data, fetch_and_store_waqi_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Fetch live telemetry on boot
    print("[Startup] Triggering live telemetry ingestion sweep...")
    try:
        fetch_and_store_owm_data()
        fetch_and_store_waqi_data()
    except Exception as e:
        print(f"[Startup Error] Ingestion failed: {e}")
    yield
    # Shutdown (if any cleanup is needed)


init_db()  # Ensure the database and tables are initialized before the app starts

app = FastAPI(
    title="LahorePulse API",
    description="Air Quality and Hazard Telemetry Engine for Lahore (LexHack 2026)",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include Routers
app.include_router(zones.router)
app.include_router(telemetry.router)
app.include_router(reports.router)


@app.get("/api/health", tags=["Root"])
def root_health_check():
    return {
        "status": "online",
        "project": "LahorePulse Telemetry Engine",
        "event": "LexHack 2026",
        "docs_url": "/docs",
    }


@app.get("/", tags=["Root"])
def root_redirect():
    return RedirectResponse(url="/static/index.html")
