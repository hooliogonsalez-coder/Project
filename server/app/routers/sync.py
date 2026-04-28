from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.database import get_session
from app.models.employee import Employee
from app.models.room import Room
from app.middleware.auth import verify_api_key
from pydantic import BaseModel

router = APIRouter(prefix="/api/sync", tags=["sync"])


class SyncRequest(BaseModel):
    since: str


class SyncResponse(BaseModel):
    employees: list
    rooms: list
    server_time: str


@router.post("/", response_model=SyncResponse)
async def sync(
    data: SyncRequest,
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_session),
):
    since_dt = datetime.fromisoformat(data.since)

    result = await db.execute(
        select(Employee).where(Employee.updated_at > since_dt)
    )
    employees = result.scalars().all()

    result = await db.execute(
        select(Room).where(Room.updated_at > since_dt)
    )
    rooms = result.scalars().all()

    return SyncResponse(
        employees=[{"id": e.id, "name": e.name, "surname": e.surname} for e in employees],
        rooms=[{"id": r.id, "room_number": r.room_number} for r in rooms],
        server_time=datetime.utcnow().isoformat(),
    )