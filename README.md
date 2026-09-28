# lahore-air-telemetry# LahorePulse - LexHack 2026 Submission

LahorePulse is a real-time hazard telemetry engine designed to combat urban smog and illegal waste burning. It provides a closed-loop platform connecting citizen reports directly with municipal dispatch using EXIF-verified geotagging.

## Features
- **Role-Based Workflows:** Distinct interfaces for Citizens (reporting) and Municipal Officials (triage & dispatch).
- **Interactive GIS Mapping:** Live Leaflet.js map tracking regional air quality and hazard hotspots.
- **Verified Crowd-Sourcing:** Enforces image uploads for EXIF metadata verification to prevent false reports.
- **Automated Dispatch:** Real-time Discord webhook integration for instant emergency alerts to city authorities.

## Tech Stack
- **Frontend:** React.js, Tailwind CSS, Leaflet.js, Chart.js
- **Backend:** Python, FastAPI, Uvicorn, Pydantic
- **Database:** SQLite (SQLAlchemy ORM)

## How to Run Locally

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn main:app --reload