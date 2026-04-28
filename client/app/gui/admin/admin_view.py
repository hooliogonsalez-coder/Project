import customtkinter as ctk
from app.gui.admin.employees_tab import EmployeesTab
from app.gui.admin.rooms_tab import RoomsTab
from app.gui.admin.sync_tab import SyncTab


class AdminView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self._build_ui()

    def _build_ui(self):
        title = ctk.CTkLabel(self, text="Администратор", font=("Arial", 24))
        title.pack(pady=10)

        self._tabs = ctk.CTkTabview(self)
        self._tabs.pack(fill="both", expand=True, padx=10, pady=10)

        tab_employees = self._tabs.add("Сотрудники")
        EmployeesTab(tab_employees)

        tab_rooms = self._tabs.add("Кабинеты")
        RoomsTab(tab_rooms)

        tab_sync = self._tabs.add("Синхронизация")
        SyncTab(tab_sync)