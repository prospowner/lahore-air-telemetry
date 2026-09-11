# app/schemas/report.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReportCreate(BaseModel):
    zone_id: int
    category: str  # e.g., "Garbage Burning", "Heavy Smoke"
    description: Optional[str] = None


class ReportResponse(ReportCreate):
    id: int
    verification_status: str
    submitted_at: datetime

    class Config:
        from_attributes = True
