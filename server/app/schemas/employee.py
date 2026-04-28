import base64
from pydantic import BaseModel, field_validator
from datetime import datetime


class EmployeeCreate(BaseModel):
    name: str
    surname: str
    department: str | None = None
    position: str | None = None
    face_embedding_b64: str

    @field_validator("face_embedding_b64")
    @classmethod
    def validate_embedding(cls, v: str) -> str:
        try:
            data = base64.b64decode(v)
            assert len(data) > 32, "Embedding слишком мал"
        except Exception:
            raise ValueError("Некорректный face_embedding")
        return v


class EmployeeOut(BaseModel):
    id: int
    name: str
    surname: str
    department: str | None
    position: str | None
    face_embedding_b64: str
    updated_at: datetime

    model_config = {"from_attributes": True}