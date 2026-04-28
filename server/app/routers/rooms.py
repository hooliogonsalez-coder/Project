from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_session
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomOut
from app.middleware.auth import verify_api_key

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.get("/", response_model=list[RoomOut])
async def list_rooms(
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(select(Room))
    rooms = result.scalars().all()
    return [RoomOut.model_validate(r) for r in rooms]


@router.post("/", response_model=RoomOut, status_code=201)
async def create_room(
    data: RoomCreate,
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_session),
):
    room = Room(
        room_number=data.room_number,
        description=data.description,
    )
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return RoomOut.model_validate(room)


@router.put("/{room_id}", response_model=RoomOut)
async def update_room(
    room_id: int,
    data: RoomCreate,
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_session),
):
    room = await db.get(Room, room_id)
    if not room:
        raise HTTPException(404, "Кабинет не найден")
    room.room_number = data.room_number
    room.description = data.description
    await db.commit()
    await db.refresh(room)
    return RoomOut.model_validate(room)


@router.delete("/{room_id}", status_code=204)
async def delete_room(
    room_id: int,
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_session),
):
    room = await db.get(Room, room_id)
    if not room:
        raise HTTPException(404, "Кабинет не найден")
    await db.delete(room)
    await db.commit()