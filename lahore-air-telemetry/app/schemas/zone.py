# app/schemas/zone.py
from datetime import datetime

from pydantic import BaseModel


class ZoneBase(BaseModel):
    name: str
    latitude: float
    longitude: float


class ZoneResponse(ZoneBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
