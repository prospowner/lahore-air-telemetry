# app/routers/telemetry.py
from typing import List

from app.database import get_db
from app.models.telemetry import TelemetryLog
from app.models.zone import Zone
from app.schemas.telemetry import TelemetryResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/telemetry", tags=["Telemetry"])


def get_aqi_details(aqi: int, source: str):
    # If it's OpenWeatherMap's 1-5 scale, map it to label/color directly
    if source == "openweathermap":
        mapping = {
            1: {"label": "Good", "color": "bg-green-500 text-white"},
            2: {"label": "Fair", "color": "bg-yellow-400 text-black"},
            3: {"label": "Moderate", "color": "bg-orange-400 text-white"},
            4: {"label": "Poor", "color": "bg-red-500 text-white"},
            5: {"label": "Very Poor", "color": "bg-purple-900 text-white"},
        }
        return mapping.get(aqi, {"label": "Unknown", "color": "bg-gray-500 text-white"})

    # Standard EPA scale for WAQI
    if aqi <= 50:
        return {"label": "Good", "color": "bg-green-500 text-white"}
    elif aqi <= 100:
        return {"label": "Moderate", "color": "bg-yellow-400 text-black"}
    elif aqi <= 150:
        return {
            "label": "Unhealthy for Sensitive Groups",
            "color": "bg-orange-500 text-white",
        }
    elif aqi <= 200:
        return {"label": "Unhealthy", "color": "bg-red-500 text-white"}
    elif aqi <= 300:
        return {"label": "Very Unhealthy", "color": "bg-purple-600 text-white"}
    else:
        return {"label": "Hazardous", "color": "bg-rose-900 text-white"}


@router.get("/zone/{zone_id}", response_model=List[TelemetryResponse])
def get_zone_telemetry(zone_id: int, db: Session = Depends(get_db)):
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    logs = (
        db.query(TelemetryLog)
        .filter(TelemetryLog.zone_id == zone_id)
        .order_by(desc(TelemetryLog.source == "waqi"), desc(TelemetryLog.recorded_at))
        .all()
    )

    response_data = []
    for log in logs:
        details = get_aqi_details(log.aqi, log.source)
        response_data.append(
            {
                "id": log.id,
                "zone_id": log.zone_id,
                "aqi": log.aqi,
                "pm2_5": log.pm2_5,
                "pm10": log.pm10,
                "source": log.source,
                "recorded_at": log.recorded_at,
                "status_label": details["label"],
                "status_color": details["color"],
            }
        )

    return response_data
