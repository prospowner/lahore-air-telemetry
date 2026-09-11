# app/routers/telemetry.py
from typing import List

from app.database import get_db
from app.models.telemetry import TelemetryLog
from app.models.zone import Zone
from app.schemas.telemetry import TelemetryResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/telemetry", tags=["Telemetry"])


@router.get("/zone/{zone_id}", response_model=List[TelemetryResponse])
def get_zone_telemetry(zone_id: int, db: Session = Depends(get_db)):
    """Retrieve historical and live telemetry logs for a specific zone."""
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    logs = (
        db.query(TelemetryLog)
        .filter(TelemetryLog.zone_id == zone_id)
        .order_by(TelemetryLog.recorded_at.desc())
        .all()
    )
    return logs
