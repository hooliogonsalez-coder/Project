import customtkinter as ctk
import threading
from app.core.db import get_connection
from app.core.api_client import APIClient
from app.config import settings


class SyncTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self._build_ui()

    def _build_ui(self):
        title = ctk.CTkLabel(self, text="Синхронизация", font=("Arial", 18))
        title.pack(pady=10)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=5)

        ctk.CTkButton(btn_frame, text="Синхронизировать", command=self._sync).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Полная синхронизация", command=self._full_sync).pack(side="left", padx=5)

        self._status = ctk.CTkLabel(self, text="Нажмите кнопку для синхронизации")
        self._status.pack(pady=10)

    def _sync(self):
        self._status.configure(text="Синхронизация...")
        threading.Thread(target=self._sync_async, daemon=True).start()

    def _sync_async(self):
        try:
            conn = get_connection(settings.SQLITE_DB_PATH, settings.SQLITE_KEY)
            cursor = conn.execute("SELECT value FROM sync_meta WHERE key = 'last_sync_at'")
            row = cursor.fetchone()
            since = row[0] if row else "1970-01-01T00:00:00"

            api = APIClient()
            data = api.sync(since)

            for emp in data.get("employees", []):
                conn.execute(
                    "INSERT OR REPLACE INTO employees (id, name, surname, department, position, face_embedding, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (emp["id"], emp["name"], emp["surname"], emp.get("department"), emp.get("position"), emp.get("face_embedding_b64", b""), emp.get("updated_at")),
                )
            for room in data.get("rooms", []):
                conn.execute(
                    "INSERT OR REPLACE INTO rooms (id, room_number, description, is_active, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (room["id"], room["room_number"], room.get("description"), room.get("is_active", 1), room.get("updated_at")),
                )
            import datetime
            conn.execute("INSERT OR REPLACE INTO sync_meta (key, value) VALUES ('last_sync_at', ?)", (datetime.datetime.utcnow().isoformat(),))
            conn.commit()
            api.close()

            self.after(0, lambda: self._status.configure(text=f"Синхронизация завершена: {len(data.get('employees', []))} сотрудников"))
        except Exception as e:
            self.after(0, lambda: self._status.configure(text=f"Ошибка: {e}"))

    def _full_sync(self):
        self._status.configure(text="Полная синхронизация...")
        threading.Thread(target=self._full_sync_async, daemon=True).start()

    def _full_sync_async(self):
        try:
            api = APIClient()
            employees = api.get_employees()
            rooms = api.get_rooms()

            conn = get_connection(settings.SQLITE_DB_PATH, settings.SQLITE_KEY)

            for emp in employees:
                conn.execute(
                    "INSERT OR REPLACE INTO employees (id, name, surname, department, position, face_embedding, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (emp["id"], emp["name"], emp["surname"], emp.get("department"), emp.get("position"), emp.get("face_embedding_b64", b""), emp.get("updated_at")),
                )
            for room in rooms:
                conn.execute(
                    "INSERT OR REPLACE INTO rooms (id, room_number, description, is_active, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (room["id"], room["room_number"], room.get("description"), room.get("is_active", 1), room.get("updated_at")),
                )
            import datetime
            conn.execute("INSERT OR REPLACE INTO sync_meta (key, value) VALUES ('last_sync_at', ?)", (datetime.datetime.utcnow().isoformat(),))
            conn.commit()
            api.close()

            self.after(0, lambda: self._status.configure(text=f"Загружено: {len(employees)} сотрудников, {len(rooms)} кабинетов"))
        except Exception as e:
            self.after(0, lambda: self._status.configure(text=f"Ошибка: {e}"))