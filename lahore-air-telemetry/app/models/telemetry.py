# app/models/telemetry.py
from datetime import datetime, timezone

from app.database import Base
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    aqi = Column(Integer, nullable=False)
    pm2_5 = Column(Float, nullable=False)
    pm10 = Column(Float, nullable=False)
    source = Column(String, nullable=False)  # e.g., "openweathermap" or "waqi"
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    zone = relationship("Zone", back_populates="telemetry_logs")
