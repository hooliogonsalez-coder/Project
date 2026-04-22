import logging
from typing import Optional

from core.interfaces import KeyRepository
from models import Employee, Key

logger = logging.getLogger(__name__)


class KeyService:
    def __init__(self, key_repo: KeyRepository):
        self._key_repo = key_repo

    def get_all_keys(self) -> list[Key]:
        return self._key_repo.get_all()

    def issue_key(self, cabinet: str, employee: Optional[Employee]) -> tuple[bool, str]:
        if employee is None:
            return False, "Сотрудник не распознан"

        key = self._key_repo.get_by_cabinet(cabinet)
        if key is None:
            return False, f"Ключ от кабинета {cabinet} не найден"

        if not key.is_available():
            return False, f"Ключ от кабинета {cabinet} уже выдан"

        if not employee.can_access(cabinet):
            return False, f"Нет доступа к кабинету {cabinet}"

        key.status = Key.from_issued(employee.id, employee.name)
        self._key_repo.update(key)
        logger.info(f"Ключ {cabinet} выдан сотруднику {employee.name}")
        return True, f"Ключ от кабинета {cabinet} выдан"

    def return_key(self, cabinet: str) -> tuple[bool, str]:
        key = self._key_repo.get_by_cabinet(cabinet)
        if key is None:
            return False, f"Ключ от кабинета {cabinet} не найден"

        if key.is_available():
            return False, f"Ключ от кабинета {cabinet} уже свободен"

        key.status = Key.from_available()
        self._key_repo.update(key)
        logger.info(f"Ключ {cabinet} возвращён")
        return True, f"Ключ от кабинета {cabinet} принят"

    def return_all_for_employee(self, employee: Employee) -> list[str]:
        returned = []
        for key in self._key_repo.get_all():
            if key.holder_id == employee.id:
                key.status = Key.from_available()
                self._key_repo.update(key)
                returned.append(key.cabinet)
        return returned