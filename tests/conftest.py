import pytest
import sqlite3
from models import Employee, Key
from core.container import Container
from core.interfaces import KeyRepository, EmployeeRepository
from database import Database


class MockKeyRepository(KeyRepository):
    def __init__(self):
        self._keys = {}
    
    def get_all(self) -> list[Key]:
        return list(self._keys.values())
    
    def get_by_cabinet(self, cabinet: str) -> Key | None:
        return self._keys.get(cabinet)
    
    def add(self, cabinet: str) -> None:
        self._keys[cabinet] = Key.from_available(cabinet)
    
    def update(self, key: Key) -> None:
        self._keys[key.cabinet] = key
    
    def delete(self, cabinet: str) -> None:
        self._keys.pop(cabinet, None)


class MockEmployeeRepository(EmployeeRepository):
    def __init__(self):
        self._employees = {}
    
    def get_by_id(self, emp_id: int) -> Employee | None:
        for emp in self._employees.values():
            if emp.id == emp_id:
                return emp
        return None
    
    def find_by_face(self, encoding: bytes, threshold: float = 0.6) -> Employee | None:
        return None
    
    def get_all(self) -> list[Employee]:
        return list(self._employees.values())
    
    def add(self, full_name: str, position: str, encoding=None, photo=None) -> int:
        emp_id = len(self._employees) + 1
        self._employees[emp_id] = Employee(emp_id, full_name, position)
        return emp_id
    
    def update(self, emp_id: int, name=None, position=None, encoding=None, photo=None) -> None:
        pass
    
    def delete(self, emp_id: int) -> None:
        pass


@pytest.fixture
def container():
    c = Container()
    c.register_instance(KeyRepository, MockKeyRepository())
    c.register_instance(EmployeeRepository, MockEmployeeRepository())
    return c


@pytest.fixture
def mock_key_repo(container):
    return container.get(KeyRepository)


@pytest.fixture
def mock_emp_repo(container):
    return container.get(EmployeeRepository)