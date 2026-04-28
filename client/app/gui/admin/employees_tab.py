import customtkinter as ctk
from app.core.db import get_connection
from app.core.api_client import APIClient
from app.config import settings


class EmployeesTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self._build_ui()
        self._load_employees()

    def _build_ui(self):
        title = ctk.CTkLabel(self, text="Сотрудники", font=("Arial", 18))
        title.pack(pady=10)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=5)

        ctk.CTkButton(btn_frame, text="Добавить", command=self._add_employee).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Обновить", command=self._load_employees).pack(side="left", padx=5)

        self._table = ctk.CTkScrollableFrame(self, label_text="Список сотрудников")
        self._table.pack(fill="both", expand=True, padx=10, pady=10)

    def _add_employee(self):
        from app.gui.admin.register_form import RegisterForm
        RegisterForm(self.winfo_toplevel(), None)

    def _load_employees(self):
        for widget in self._table.winfo_children():
            widget.destroy()

        headers = ["ID", "Имя", "Фамилия", "Подразделение", "Должность"]
        header_frame = ctk.CTkFrame(self._table)
        header_frame.pack(fill="x", pady=2)
        for i, h in enumerate(headers):
            ctk.CTkLabel(header_frame, text=h, font=("Arial", 12, "bold"), width=20).pack(side="left", padx=5)

        try:
            conn = get_connection(settings.SQLITE_DB_PATH, settings.SQLITE_KEY)
            cursor = conn.execute("SELECT id, name, surname, department, position FROM employees ORDER BY surname")
            for row in cursor:
                row_frame = ctk.CTkFrame(self._table)
                row_frame.pack(fill="x", pady=2)
                for col in row:
                    ctk.CTkLabel(row_frame, text=str(col), width=20).pack(side="left", padx=5)
        except Exception as e:
            ctk.CTkLabel(self._table, text=f"Ошибка загрузки: {e}").pack()