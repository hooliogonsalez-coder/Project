from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, func
from app.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(String(500))
    is_active = Column(SmallInteger, nullable=False, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())