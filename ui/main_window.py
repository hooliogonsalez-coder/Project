from abc import ABC
import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional

import config
from core.container import Container
from core.interfaces import EmployeeRepository, KeyRepository, FaceRecognizer
from services import CameraService, FaceService, KeyService
from database import Database
from data import DataStore
from ui import VideoPanel, EmployeeCard, KeysTable, EventLog, AddEmployeeDialog, AddKeyDialog
try:
    from app_container import create_container
except ImportError:
    create_container = None

logger = logging.getLogger(__name__)


class StyledButton(tk.Button):
    def __init__(self, parent, text, command, bg=config.BUTTON_COLOR, **kwargs):
        super().__init__(parent, text=text, command=command, 
                         bg=bg, fg="white", font=config.FONT_BUTTON,
                         relief=tk.FLAT, bd=0, padx=20, pady=10, **kwargs)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self._default_bg = bg

    def _on_enter(self, event):
        self.config(bg=config.BUTTON_HOVER, cursor="hand2")

    def _on_leave(self, event):
        self.config(bg=self._default_bg)


class MainWindow:
    def __init__(self, root: tk.Tk, container: Optional[Container] = None):
        self._root = root
        self._root.title(config.WINDOW_TITLE)
        self._root.geometry(config.WINDOW_GEOMETRY)
        self._root.configure(bg=config.BG_COLOR)
        self._root.protocol("WM_DELETE_WINDOW", self._on_closing)

        if container is None and create_container is not None:
            container = create_container()
        
        self._container = container
        
        if container:
            self._db = container.get(Database)
            self._store = container.get(DataStore)
            self._key_service = container.get(KeyService)
            self._face_service = container.get(FaceService)
            self._camera_service = container.get(CameraService)
        else:
            self._db = Database(config.DATABASE_PATH)
            self._store = DataStore(self._db)
            self._camera_service = CameraService()
            self._key_service = KeyService(self._store)
            self._face_service = FaceService(self._store)

        self._setup_ui()
        self._init_camera()
        self._update_video()

    def _setup_ui(self):
        main_frame = tk.Frame(self._root, bg=config.BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        top_frame = tk.Frame(main_frame, bg=config.BG_COLOR)
        top_frame.pack(fill=tk.X, pady=(0, 15))

        title = tk.Label(top_frame, text="🔐 Контроль выдачи ключей", 
                         font=config.FONT_TITLE, bg=config.BG_COLOR, fg=config.ACCENT_COLOR)
        title.pack(side=tk.LEFT)

        cam_status_frame = tk.Frame(top_frame, bg=config.BG_COLOR)
        cam_status_frame.pack(side=tk.RIGHT)

        self._cam_indicator = tk.Canvas(cam_status_frame, width=16, height=16, 
                                        bg=config.BG_COLOR, highlightthickness=0)
        self._cam_indicator.pack(side=tk.LEFT, padx=8)
        self._cam_indicator.create_oval(2, 2, 14, 14, fill="#94a3b8", outline="")

        self._cam_status_label = tk.Label(cam_status_frame, text="Камера", 
                                           font=config.FONT_SMALL, bg=config.BG_COLOR, fg="#64748b")
        self._cam_status_label.pack(side=tk.LEFT)

        select_cam_btn = tk.Button(cam_status_frame, text="📷", 
                                   command=self._show_camera_selector,
                                   bg=config.BG_COLOR, fg=config.ACCENT_COLOR,
                                   font=("Segoe UI", 14), relief=tk.FLAT, bd=0, highlightthickness=0)
        select_cam_btn.pack(side=tk.LEFT, padx=(10, 0))

        columns_frame = tk.Frame(main_frame, bg=config.BG_COLOR)
        columns_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(columns_frame, bg=config.BG_COLOR)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))

        self._video_panel = VideoPanel(left_frame)
        self._video_panel.frame.pack(fill=tk.X, pady=(0, 10))

        self._employee_card = EmployeeCard(left_frame)
        self._employee_card.frame.pack(fill=tk.X, pady=(0, 10))

        btn_frame = tk.Frame(left_frame, bg=config.BG_COLOR)
        btn_frame.pack(fill=tk.X)

        self._issue_btn = StyledButton(btn_frame, text="📤 ВЫДАТЬ КЛЮЧ", 
                                        command=self._issue_key, bg=config.BUTTON_COLOR)
        self._issue_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        self._return_btn = StyledButton(btn_frame, text="📥 ПРИНЯТЬ КЛЮЧ", 
                                         command=self._return_key, bg=config.SUCCESS_COLOR)
        self._return_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        add_emp_frame = tk.Frame(left_frame, bg=config.BG_COLOR)
        add_emp_frame.pack(fill=tk.X, pady=(10, 0))

        self._add_employee_btn = StyledButton(add_emp_frame, text="➕ ДОБАВИТЬ СОТРУДНИКА", 
                                                command=self._add_employee, bg=config.ACCENT_COLOR)
        self._add_employee_btn.pack(fill=tk.X)

        center_frame = tk.Frame(columns_frame, bg=config.BG_COLOR)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self._keys_table = KeysTable(center_frame, delete_callback=self._delete_key)
        self._keys_table.frame.pack(fill=tk.BOTH, expand=True)
        self._keys_table.update_keys(self._key_service.get_all_keys())
        
        keys_btn_frame = tk.Frame(center_frame, bg=config.BG_COLOR)
        keys_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        add_key_btn = StyledButton(keys_btn_frame, text="➕ ДОБАВИТЬ КАБИНЕТ", 
                                    command=self._add_key, bg=config.ACCENT_COLOR)
        add_key_btn.pack(fill=tk.X)

        right_frame = tk.Frame(columns_frame, bg=config.BG_COLOR)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(10, 0))

        self._event_log = EventLog(right_frame)
        self._event_log.frame.pack(fill=tk.BOTH, expand=True)
        self._event_log.log("✅ Система запущена")

        recognize_btn = StyledButton(main_frame, text="👁 РАСПОЗНАТЬ ЛИЦО", 
                                      command=self._recognize_face, bg=config.ACCENT_COLOR)
        recognize_btn.pack(fill=tk.X, ipady=10, pady=(15, 0))

    def _init_camera(self):
        available = self._camera_service.get_available_cameras()
        if available:
            index = int(available[0].split()[0])
            if self._camera_service.init_camera(index):
                self._update_cam_indicator(True)

    def _show_camera_selector(self):
        if hasattr(self, '_camera_combo') and self._camera_combo:
            self._camera_combo.destroy()

        available = self._camera_service.get_available_cameras()
        self._camera_combo = ttk.Combobox(
            self._root, values=available, state="readonly", width=10
        )
        current_str = str(self._camera_service.current_index)
        if current_str in available:
            self._camera_combo.set(current_str)
        else:
            self._camera_combo.set(available[0])

        self._camera_combo.bind("<<ComboboxSelected>>", lambda e: self._switch_camera(self._camera_combo.get()))
        self._camera_combo.place(relx=0.9, rely=0.05, anchor='center')

    def _switch_camera(self, index_str: str):
        if self._camera_service.switch_camera(index_str):
            self._update_cam_indicator(True)
            self._event_log.log(f"Камера переключена на {index_str}", "success")
        else:
            self._update_cam_indicator(False)
            self._event_log.log(f"Не удалось подключить камеру {index_str}", "error")

    def _update_cam_indicator(self, is_ok: bool):
        color = config.SUCCESS_COLOR if is_ok else config.ERROR_COLOR
        self._cam_indicator.delete("all")
        self._cam_indicator.create_oval(2, 2, 14, 14, fill=color, outline="")
        status_text = "Подключена" if is_ok else "Отключена"
        self._cam_status_label.config(text=f"Камера: {status_text}", 
                                        fg=config.SUCCESS_COLOR if is_ok else config.ERROR_COLOR)

    def _update_video(self):
        frame = self._camera_service.read_frame()
        self._video_panel.update_frame(frame)
        self._root.after(config.VIDEO_UPDATE_INTERVAL_MS, self._update_video)

    def _recognize_face(self):
        frame = self._camera_service.read_frame()
        if frame is None:
            self._event_log.log("Камера недоступна", "error")
            return

        self._event_log.log("Распознавание...", "info")
        employee = self._face_service.recognize(frame)
        if employee:
            self._employee_card.update_employee(employee)
            self._event_log.log(f"Распознан: {employee.name}", "success")
        else:
            self._event_log.log("Лицо не распознано", "warning")

    def _issue_key(self):
        employee = self._face_service.current_employee
        cabinet = self._keys_table.get_selected_cabinet()

        if not employee:
            self._event_log.log("Сотрудник не распознан", "error")
            return

        if not cabinet:
            self._event_log.log("Выберите ключ в таблице", "warning")
            return

        success, message = self._key_service.issue_key(cabinet, employee)
        level = "success" if success else "error"
        self._event_log.log(message, level)
        if success:
            self._keys_table.update_keys(self._key_service.get_all_keys())

    def _return_key(self):
        cabinet = self._keys_table.get_selected_cabinet()

        if not cabinet:
            self._event_log.log("Выберите ключ в таблице", "warning")
            return

        success, message = self._key_service.return_key(cabinet)
        level = "success" if success else "error"
        self._event_log.log(message, level)
        if success:
            self._keys_table.update_keys(self._key_service.get_all_keys())

    def _add_employee(self):
        dialog = AddEmployeeDialog(self._root, self._face_service, self._camera_service, self._on_employee_added)

    def _add_key(self):
        dialog = AddKeyDialog(self._root, self._store, self._on_key_added)

    def _on_key_added(self, cabinet):
        self._keys_table.update_keys(self._key_service.get_all_keys())
        self._event_log.log(f"Добавлен кабинет: {cabinet}", "success")

    def _delete_key(self, cabinet):
        key = self._store.get_key(cabinet)
        if key and not key.is_available():
            self._event_log.log(f"Нельзя удалить: ключ {cabinet} выдан", "error")
            return
        
        result = tk.messagebox.askyesno(
            "Подтверждение", 
            f"Удалить кабинет {cabinet}?",
            parent=self._root
        )
        if result:
            self._store.delete_key(cabinet)
            self._keys_table.update_keys(self._key_service.get_all_keys())
            self._event_log.log(f"Удалён кабинет: {cabinet}", "success")

    def _on_employee_added(self, emp_id, name, position):
        self._event_log.log(f"Добавлен сотрудник: {name} (ID: {emp_id})", "success")

    def _on_closing(self):
        self._camera_service.release()
        self._db.close()
        self._root.destroy()
