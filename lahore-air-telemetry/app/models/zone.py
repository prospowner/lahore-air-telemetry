# app/models/zone.py
from datetime import datetime, timezone

from app.database import Base
from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.orm import relationship


# Define the Zone model
class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    telemetry_logs = relationship(
        "TelemetryLog", back_populates="zone", cascade="all, delete-orphan"
    )
    reports = relationship(
        "Report", back_populates="zone", cascade="all, delete-orphan"
    )
