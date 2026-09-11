# app/models/report.py
from datetime import datetime, timezone

from app.database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship


# Define the Report model
class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    category = Column(String, nullable=False)  # e.g., "Garbage Burning", "Heavy Smoke"
    description = Column(Text, nullable=True)
    verification_status = Column(
        String, default="pending"
    )  # pending, verified, dismissed
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    zone = relationship("Zone", back_populates="reports")
