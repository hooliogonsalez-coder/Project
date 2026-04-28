from PIL import Image, ImageTk
import customtkinter as ctk
import cv2
import threading
import time


class TerminalView(ctk.CTkFrame):
    RECOGNITION_INTERVAL_MS = 500

    def __init__(self, master):
        super().__init__(master)
        self.camera = None
        self.biometric = None
        self.room_manager = None
        self.lock_driver = None
        self.db_conn = None
        self._last_employee_id = None

        self._canvas = ctk.CTkLabel(self, text="")
        self._canvas.pack(fill="both", expand=True)

        self._status = ctk.CTkLabel(self, text="Ожидание лица...", font=("Arial", 24))
        self._status.pack()

        self._room_label = ctk.CTkLabel(self, text="", font=("Arial", 16))
        self._room_label.pack()

        self._init_components()
        self._schedule_recognition()

    def _init_components(self):
        from app.core.camera import CameraThread
        from app.core.biometric import FaceRecognizer
        from app.core.room_manager import RoomManager
        from app.core.lock_driver import create_lock_driver
        from app.core.db import get_connection
        from app.core.db import init_db
        from app.config import settings

        self.camera = CameraThread(source=settings.CAMERA_SOURCE, fps=settings.CAMERA_FPS)
        self.camera.start()

        self.biometric = FaceRecognizer(
            model_name=settings.FACE_MODEL,
            threshold=settings.FACE_RECOGNITION_THRESHOLD,
        )

        self.room_manager = RoomManager(timeout_minutes=settings.ROOM_TIMEOUT_MINUTES)

        self.lock_driver = create_lock_driver(settings)

        self.db_conn = get_connection(settings.SQLITE_DB_PATH, settings.SQLITE_KEY)
        init_db(self.db_conn)

        self._load_data()

    def _load_data(self):
        cursor = self.db_conn.execute("SELECT id, room_number, is_active FROM rooms WHERE is_active = 1")
        rooms = [{"id": r[0], "room_number": r[1], "is_active": r[2]} for r in cursor]
        self.room_manager.load_rooms(rooms)

        cursor = self.db_conn.execute("SELECT id, name, surname, department, position, face_embedding FROM employees")
        employees = [
            {
                "id": e[0],
                "name": e[1],
                "surname": e[2],
                "department": e[3],
                "position": e[4],
                "face_embedding": e[5],
            }
            for e in cursor
        ]
        self.biometric.load_from_db(employees)

    def _schedule_recognition(self):
        threading.Thread(target=self._recognition_loop, daemon=True).start()

    def _recognition_loop(self):
        while True:
            frame = self.camera.get_frame()
            if frame is not None:
                self._process_frame(frame)
            time.sleep(self.RECOGNITION_INTERVAL_MS / 1000)

    def _process_frame(self, frame):
        embedding = self.biometric.detect_and_embed(frame)
        if embedding is None:
            self.after(0, lambda: self._status.configure(text="Ожидание лица..."))
            return

        employee_id = self.biometric.identify(embedding)
        if employee_id is None:
            self.after(0, lambda: self._status.configure(text="Неизвестный сотрудник"))
            return

        cursor = self.db_conn.execute(
            "SELECT name, surname FROM employees WHERE id = ?",
            (employee_id,)
        )
        row = cursor.fetchone()
        if not row:
            return

        full_name = f"{row[0]} {row[1]}"

        if self.room_manager.has_employee_room(employee_id):
            self.room_manager.release_by_employee(employee_id)
            self.after(0, lambda: self._status.configure(text=f"{full_name} — ключ возвращён"))
            self.after(0, lambda: self._room_label.configure(text=""))
            return

        room = self.room_manager.assign(employee_id)
        if room is None:
            self.after(0, lambda: self._status.configure(text=f"{full_name} — нет свободных кабинетов"))
            return

        threading.Thread(
            target=lambda: self.lock_driver.open(room["room_number"]),
            daemon=True
        ).start()

        self.after(0, lambda: self._status.configure(text=f"{full_name} → Кабинет {room['room_number']}"))
        self.after(0, lambda: self._room_label.configure(text=f"Занят: {room['room_number']}"))

    def destroy(self):
        if self.camera:
            self.camera.stop()
        super().destroy()