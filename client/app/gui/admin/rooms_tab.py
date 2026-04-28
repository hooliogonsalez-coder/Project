import customtkinter as ctk
from app.core.db import get_connection
from app.config import settings


class RoomsTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self._build_ui()
        self._load_rooms()

    def _build_ui(self):
        title = ctk.CTkLabel(self, text="Кабинеты", font=("Arial", 18))
        title.pack(pady=10)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=5)

        ctk.CTkButton(btn_frame, text="Добавить", command=self._add_room).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Обновить", command=self._load_rooms).pack(side="left", padx=5)

        self._table = ctk.CTkScrollableFrame(self, label_text="Список кабинетов")
        self._table.pack(fill="both", expand=True, padx=10, pady=10)

    def _add_room(self):
        dialog = ctk.CTkInputDialog(title="Новый кабинет", text="Номер кабинета:")
        room_number = dialog.get_input()
        if room_number:
            try:
                conn = get_connection(settings.SQLITE_DB_PATH, settings.SQLITE_KEY)
                conn.execute("INSERT INTO rooms (room_number, is_active) VALUES (?, 1)", (room_number,))
                conn.commit()
                self._load_rooms()
            except Exception as e:
                print(f"Error: {e}")

    def _load_rooms(self):
        for widget in self._table.winfo_children():
            widget.destroy()

        headers = ["ID", "Номер", "Описание", "Активен"]
        header_frame = ctk.CTkFrame(self._table)
        header_frame.pack(fill="x", pady=2)
        for i, h in enumerate(headers):
            ctk.CTkLabel(header_frame, text=h, font=("Arial", 12, "bold"), width=20).pack(side="left", padx=5)

        try:
            conn = get_connection(settings.SQLITE_DB_PATH, settings.SQLITE_KEY)
            cursor = conn.execute("SELECT id, room_number, description, is_active FROM rooms ORDER BY room_number")
            for row in cursor:
                row_frame = ctk.CTkFrame(self._table)
                row_frame.pack(fill="x", pady=2)
                for col in row:
                    ctk.CTkLabel(row_frame, text=str(col), width=20).pack(side="left", padx=5)
        except Exception as e:
            ctk.CTkLabel(self._table, text=f"Ошибка загрузки: {e}").pack()