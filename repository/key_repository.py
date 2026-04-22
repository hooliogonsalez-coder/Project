import logging
from typing import Optional

from core.interfaces import KeyRepository
from database import Database
from models import Key, KeyStatus

logger = logging.getLogger(__name__)


class KeyRepositoryImpl(KeyRepository):
    def __init__(self, db: Database):
        self._db = db

    def get_all(self) -> list[Key]:
        key_rows = self._db.get_all_keys()
        keys = []
        for row in key_rows:
            status_str = row.get("status", "AVAILABLE")
            status = KeyStatus.ISSUED if status_str == "ISSUED" else KeyStatus.AVAILABLE
            keys.append(Key(
                cabinet=row["cabinet"],
                status=status,
                holder_id=row.get("holder_id"),
                holder_name=row.get("holder_name")
            ))
        return keys

    def get_by_cabinet(self, cabinet: str) -> Optional[Key]:
        row = self._db.get_key(cabinet)
        if row:
            status_str = row.get("status", "AVAILABLE")
            status = KeyStatus.ISSUED if status_str == "ISSUED" else KeyStatus.AVAILABLE
            return Key(
                cabinet=row["cabinet"],
                status=status,
                holder_id=row.get("holder_id"),
                holder_name=row.get("holder_name")
            )
        return None

    def add(self, cabinet: str) -> None:
        self._db.add_key(cabinet)

    def update(self, key: Key) -> None:
        status_str = key.status.value
        holder_id = key.holder_id
        holder_name = key.holder_name
        self._db.update_key(key.cabinet, status_str, holder_id, holder_name)

    def delete(self, cabinet: str) -> None:
        self._db.delete_key(cabinet)