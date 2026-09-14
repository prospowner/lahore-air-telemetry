from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReportCreate(BaseModel):
    zone_id: int
    category: str  # e.g., "Garbage Burning", "Heavy Smoke"
    description: Optional[str] = None


class ReportResponse(ReportCreate):
    id: int
    image_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    upvotes: int
    downvotes: int
    verification_status: str
    moderation_status: str
    submitted_at: datetime

    class Config:
        from_attributes = True
