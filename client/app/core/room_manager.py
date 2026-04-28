import threading
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RoomOccupancy:
    room_id: int
    room_number: str
    employee_id: int
    assigned_at: float = field(default_factory=time.time)


class RoomManager:
    def __init__(self, timeout_minutes: int = 480):
        self._lock = threading.Lock()
        self._rooms: dict[int, dict] = {}
        self._occupied: dict[int, RoomOccupancy] = {}
        self._employee_room: dict[int, int] = {}
        self.timeout_seconds = timeout_minutes * 60

    def has_employee_room(self, employee_id: int) -> bool:
        with self._lock:
            return employee_id in self._employee_room

    def load_rooms(self, rooms: list[dict]):
        with self._lock:
            self._rooms = {r["id"]: r for r in rooms if r["is_active"] == 1}
            self._occupied.clear()
            self._employee_room.clear()

    def assign(self, employee_id: int) -> Optional[dict]:
        with self._lock:
            if employee_id in self._employee_room:
                room_id = self._employee_room[employee_id]
                return self._rooms.get(room_id)

            free_rooms = [
                r for rid, r in self._rooms.items()
                if rid not in self._occupied
            ]
            if not free_rooms:
                return None

            room = min(free_rooms, key=lambda r: r["room_number"])
            self._occupied[room["id"]] = RoomOccupancy(
                room_id=room["id"],
                room_number=room["room_number"],
                employee_id=employee_id,
            )
            self._employee_room[employee_id] = room["id"]
            return room

    def release_by_employee(self, employee_id: int) -> bool:
        with self._lock:
            room_id = self._employee_room.pop(employee_id, None)
            if room_id is None:
                return False
            self._occupied.pop(room_id, None)
            return True

    def release_by_room(self, room_id: int):
        with self._lock:
            occ = self._occupied.pop(room_id, None)
            if occ:
                self._employee_room.pop(occ.employee_id, None)

    def auto_release_expired(self):
        now = time.time()
        with self._lock:
            expired = [
                rid for rid, occ in self._occupied.items()
                if now - occ.assigned_at > self.timeout_seconds
            ]
            for rid in expired:
                occ = self._occupied.pop(rid)
                self._employee_room.pop(occ.employee_id, None)

    def get_status(self) -> list[dict]:
        with self._lock:
            result = []
            for rid, room in self._rooms.items():
                occ = self._occupied.get(rid)
                result.append({
                    "room_number": room["room_number"],
                    "occupied": occ is not None,
                    "employee_id": occ.employee_id if occ else None,
                })
            return result