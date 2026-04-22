from dataclasses import dataclass
from enum import Enum
from typing import Optional


class KeyStatus(Enum):
    ISSUED = "Выдан"
    AVAILABLE = "Свободен"


@dataclass
class Key:
    cabinet: str
    status: KeyStatus = KeyStatus.AVAILABLE
    holder_id: Optional[int] = None
    holder_name: Optional[str] = None

    @property
    def holder_display(self) -> str:
        return self.holder_name if self.holder_name else "—"

    @classmethod
    def from_issued(cls, holder_id: int, holder_name: str, cabinet: str = "") -> "Key":
        return cls(cabinet=cabinet, status=KeyStatus.ISSUED, holder_id=holder_id, holder_name=holder_name)

    @classmethod
    def from_available(cls, cabinet: str = "") -> "Key":
        return cls(cabinet=cabinet, status=KeyStatus.AVAILABLE, holder_id=None, holder_name=None)

    def is_available(self) -> bool:
        return self.status == KeyStatus.AVAILABLE
