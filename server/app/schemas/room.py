from pydantic import BaseModel
from datetime import datetime


class RoomCreate(BaseModel):
    room_number: str
    description: str | None = None


class RoomOut(BaseModel):
    id: int
    room_number: str
    description: str | None
    is_active: int
    updated_at: datetime

    model_config = {"from_attributes": True}