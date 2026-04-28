import threading
import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
from app.core.biometric import FaceRecognizer
from app.core.db import get_connection
from app.core.api_client import APIClient
from app.config import settings
from app.utils.crypto import EmbeddingCrypto


class RegisterForm(ctk.CTkToplevel):
    CAPTURE_FRAMES = 10

    def __init__(self, master, biometric: FaceRecognizer):
        super().__init__(master)
        self.title("Новый сотрудник")
        self.geometry("800x500")
        self._biometric = biometric
        self._db = None
        self._api = None
        self._captured_frames = []
        self._build_ui()

    def _build_ui(self):
        self._video_label = ctk.CTkLabel(self, text="")
        self._video_label.grid(row=0, column=0, padx=10, pady=10)

        fields = ctk.CTkFrame(self)
        fields.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        ctk.CTkLabel(fields, text="Регистрация сотрудника", font=("Arial", 16)).pack(pady=10)

        self._name_entry = ctk.CTkEntry(fields, placeholder_text="Имя", width=200)
        self._name_entry.pack(pady=5)

        self._surname_entry = ctk.CTkEntry(fields, placeholder_text="Фамилия", width=200)
        self._surname_entry.pack(pady=5)

        self._dept_entry = ctk.CTkEntry(fields, placeholder_text="Подразделение", width=200)
        self._dept_entry.pack(pady=5)

        self._pos_entry = ctk.CTkEntry(fields, placeholder_text="Должность", width=200)
        self._pos_entry.pack(pady=5)

        btn_frame = ctk.CTkFrame(fields)
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="Захватить лицо", command=self._capture).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Сохранить", command=self._save).pack(side="left", padx=5)

        self._status_label = ctk.CTkLabel(self, text="")
        self._status_label.grid(row=1, columnspan=2)

        self._start_camera_preview()

    def _start_camera_preview(self):
        from app.core.camera import CameraThread
        self.camera = CameraThread(source=settings.CAMERA_SOURCE, fps=10)
        self.camera.start()
        self._update_preview()

    def _update_preview(self):
        frame = self.camera.get_frame() if hasattr(self, 'camera') else None
        if frame is not None:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = img.resize((320, 240))
            photo = ImageTk.PhotoImage(img)
            self._video_label.configure(image=photo)
            self._video_label.image = photo
        self.after(100, self._update_preview)

    def _capture(self):
        self._captured_frames = []
        self._status_label.configure(text="Смотрите в камеру...")
        self._do_capture()

    def _do_capture(self):
        frame = self.camera.get_frame() if hasattr(self, 'camera') else None
        if frame is not None:
            self._captured_frames.append(frame)
        if len(self._captured_frames) < self.CAPTURE_FRAMES:
            self.after(100, self._do_capture)
        else:
            self._status_label.configure(text=f"Захвачено {len(self._captured_frames)} кадров")

    def _save(self):
        if not self._captured_frames:
            self._status_label.configure(text="Сначала захватите лицо")
            return

        name = self._name_entry.get()
        surname = self._surname_entry.get()
        if not name or not surname:
            self._status_label.configure(text="Имя и фамилия обязательны")
            return

        embedding = self._biometric.capture_template(self._captured_frames)
        if embedding is None:
            self._status_label.configure(text="Ошибка: лицо не обнаружено")
            return

        crypto = EmbeddingCrypto(settings.SQLITE_KEY)
        encrypted = crypto.encrypt(embedding)

        employee_data = {
            "name": name,
            "surname": surname,
            "department": self._dept_entry.get() or None,
            "position": self._pos_entry.get() or None,
            "face_embedding_b64": encrypted.hex(),
        }

        threading.Thread(target=self._save_async, args=(employee_data,), daemon=True).start()

    def _save_async(self, data):
        try:
            conn = get_connection(settings.SQLITE_DB_PATH, settings.SQLITE_KEY)
            from app.core.db import init_db
            init_db(conn)
            conn.execute(
                "INSERT INTO employees (name, surname, department, position, face_embedding) VALUES (?, ?, ?, ?, ?)",
                (data["name"], data["surname"], data["department"], data["position"], bytes.fromhex(data["face_embedding_b64"])),
            )
            conn.commit()
            self.after(0, lambda: self._status_label.configure(text="Сохранено локально"))
        except Exception as e:
            self.after(0, lambda: self._status_label.configure(text=f"Ошибка: {e}"))

        try:
            api = APIClient()
            api.create_employee(data)
            api.close()
            self.after(0, lambda: self._status_label.configure(text="Сохранено на сервере"))
        except Exception as e:
            self.after(0, lambda: self._status_label.configure(text=f"Сохранено локально (оффлайн): {e}"))

    def destroy(self):
        if hasattr(self, 'camera'):
            self.camera.stop()
        super().destroy()