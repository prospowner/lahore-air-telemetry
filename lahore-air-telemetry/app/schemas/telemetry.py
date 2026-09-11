# app/schemas/telemetry.py
from datetime import datetime

from pydantic import BaseModel


class TelemetryResponse(BaseModel):
    id: int
    zone_id: int
    aqi: int
    pm2_5: float
    pm10: float
    source: str
    recorded_at: datetime

    class Config:
        from_attributes = True
