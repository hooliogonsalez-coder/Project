from abc import ABC, abstractmethod
from typing import Optional

from models import Employee, Key


class KeyRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Key]:
        pass

    @abstractmethod
    def get_by_cabinet(self, cabinet: str) -> Optional[Key]:
        pass

    @abstractmethod
    def add(self, cabinet: str) -> None:
        pass

    @abstractmethod
    def update(self, key: Key) -> None:
        pass

    @abstractmethod
    def delete(self, cabinet: str) -> None:
        pass


class EmployeeRepository(ABC):
    @abstractmethod
    def get_by_id(self, emp_id: int) -> Optional[Employee]:
        pass

    @abstractmethod
    def find_by_face(self, face_encoding: bytes, threshold: float = 0.6) -> Optional[Employee]:
        pass

    @abstractmethod
    def get_all(self) -> list[Employee]:
        pass

    @abstractmethod
    def add(self, full_name: str, position: str, face_encoding: Optional[bytes] = None,
          photo_path: Optional[str] = None) -> int:
        pass

    @abstractmethod
    def update(self, emp_id: int, full_name: Optional[str] = None,
             position: Optional[str] = None, face_encoding: Optional[bytes] = None,
             photo_path: Optional[str] = None) -> None:
        pass

    @abstractmethod
    def delete(self, emp_id: int) -> None:
        pass


class FaceRecognizer(ABC):
    @abstractmethod
    def encode(self, image_source: bytes) -> Optional[bytes]:
        pass

    @abstractmethod
    def recognize(self, frame) -> Optional[Employee]:
        pass