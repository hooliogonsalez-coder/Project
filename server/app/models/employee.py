from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, func
from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    department = Column(String(200))
    position = Column(String(200))
    face_embedding = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())