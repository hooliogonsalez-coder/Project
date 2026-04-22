from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Employee:
    id: int
    name: str
    position: str
    access_cabinets: list[str] = field(default_factory=list)
    face_encoding: Optional[bytes] = None
    photo_path: Optional[str] = None

    @property
    def full_name(self) -> str:
        return self.name

    @property
    def access_str(self) -> str:
        return ", ".join(self.access_cabinets) if self.access_cabinets else "—"

    def can_access(self, cabinet: str) -> bool:
        return cabinet in self.access_cabinets
