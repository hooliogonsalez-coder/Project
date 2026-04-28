from datetime import datetime, timezone
from loguru import logger
from app.core.db import get_connection
from app.core.api_client import APIClient
from app.core.biometric import FaceRecognizer
from app.config import settings


class SyncManager:
    def __init__(self, api_client: APIClient, db_conn, biometric: FaceRecognizer):
        self._api = api_client
        self._db = db_conn
        self._biometric = biometric

    def startup_sync(self):
        try:
            cursor = self._db.execute("SELECT value FROM sync_meta WHERE key = 'last_sync_at'")
            row = cursor.fetchone()
            since = row[0] if row else "1970-01-01T00:00:00"

            data = self._api.sync(since)
            self._apply_changes(data)

            self._db.execute(
                "INSERT OR REPLACE INTO sync_meta (key, value) VALUES ('last_sync_at', ?)",
                (datetime.now(timezone.utc).isoformat(),)
            )
            self._db.commit()

            logger.info(f"Синхронизация: {len(data.get('employees', []))} сотрудников, {len(data.get('rooms', []))} кабинетов")
        except Exception as e:
            logger.warning(f"Нет связи с сервером, работаем офлайн: {e}")

        employees = self._load_employees()
        self._biometric.load_from_db(employees)

    def _apply_changes(self, data: dict):
        for emp in data.get("employees", []):
            self._db.execute(
                "INSERT OR REPLACE INTO employees (id, name, surname, department, position, face_embedding, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (emp.get("id"), emp.get("name"), emp.get("surname"), emp.get("department"), emp.get("position"), bytes.fromhex(emp.get("face_embedding_b64", "00")), emp.get("updated_at"))
            )
        for room in data.get("rooms", []):
            self._db.execute(
                "INSERT OR REPLACE INTO rooms (id, room_number, description, is_active, updated_at) VALUES (?, ?, ?, ?, ?)",
                (room.get("id"), room.get("room_number"), room.get("description"), room.get("is_active", 1), room.get("updated_at"))
            )
        self._db.commit()

    def _load_employees(self):
        cursor = self._db.execute("SELECT id, name, surname, department, position, face_embedding, updated_at FROM employees")
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "name": row[1],
                "surname": row[2],
                "department": row[3],
                "position": row[4],
                "face_embedding": row[5],
                "updated_at": row[6],
            }
            for row in rows
        ]

    def push_local_employee(self, employee_data: dict):
        try:
            result = self._api.create_employee(employee_data)
            self._db.execute(
                "UPDATE employees SET id = ? WHERE id = ?",
                (result.get("id"), employee_data.get("id"))
            )
            self._db.commit()
        except Exception as e:
            logger.warning(f"Не удалось отправить сотрудника на сервер: {e}")