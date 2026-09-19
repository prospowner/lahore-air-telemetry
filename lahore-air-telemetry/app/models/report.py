from app.database import Base
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


# Define the Report model with strict non-nullable database constraints
class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    category = Column(String(50), nullable=False, default="Garbage Burning")
    description = Column(
        Text, nullable=False
    )  # Enforce that a description cannot be null
    image_url = Column(
        String(255), nullable=False
    )  # Enforce that an image/EXIF source is mandatory
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    upvotes = Column(Integer, nullable=False, server_default="0")
    downvotes = Column(Integer, nullable=False, server_default="0")
    verification_status = Column(
        String(50), nullable=False, server_default="pending"
    )  # pending, verified, dismissed
    moderation_status = Column(
        String(50), nullable=False, server_default="approved"
    )  # approved, flagged
    submitted_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationship
    zone = relationship("Zone", back_populates="reports")
