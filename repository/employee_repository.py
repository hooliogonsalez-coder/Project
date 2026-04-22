import logging
from typing import Optional

from core.interfaces import EmployeeRepository
from database import Database
from models import Employee

logger = logging.getLogger(__name__)


class EmployeeRepositoryImpl(EmployeeRepository):
    def __init__(self, db: Database):
        self._db = db

    def get_by_id(self, emp_id: int) -> Optional[Employee]:
        return self._db.get_employee(emp_id)

    def find_by_face(self, face_encoding: bytes, threshold: float = 0.6) -> Optional[Employee]:
        return self._db.get_employee_by_face(face_encoding, threshold)

    def get_all(self) -> list[Employee]:
        return self._db.get_all_employees()

    def add(self, full_name: str, position: str,
            face_encoding: Optional[bytes] = None,
            photo_path: Optional[str] = None) -> int:
        return self._db.add_employee(full_name, position, face_encoding, photo_path)

    def update(self, emp_id: int, full_name: Optional[str] = None,
              position: Optional[str] = None,
              face_encoding: Optional[bytes] = None,
              photo_path: Optional[str] = None) -> None:
        self._db.update_employee(emp_id, full_name, position, face_encoding, photo_path)

    def delete(self, emp_id: int) -> None:
        self._db.delete_employee(emp_id)