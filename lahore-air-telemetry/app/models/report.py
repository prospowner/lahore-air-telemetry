# app/models/report.py
from datetime import datetime, timezone

from app.database import Base
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship


# Define the Report model
class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    category = Column(String, nullable=False)  # e.g., "Garbage Burning", "Heavy Smoke"
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    verification_status = Column(
        String, default="pending"
    )  # pending, verified, dismissed
    moderation_status = Column(String, default="approved")  # approved, flagged
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    zone = relationship("Zone", back_populates="reports")
