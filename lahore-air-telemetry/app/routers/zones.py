# app/routers/zones.py
from typing import List

from app.database import get_db
from app.models.zone import Zone
from app.schemas.zone import ZoneResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/zones", tags=["Zones"])


@router.get("/", response_model=List[ZoneResponse])
def get_zones(db: Session = Depends(get_db)):
    """Retrieve all monitored micro-neighborhood zones in Lahore."""
    zones = db.query(Zone).all()
    return zones


@router.get("/{zone_id}", response_model=ZoneResponse)
def get_zone_by_id(zone_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific zone by its ID."""
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone
