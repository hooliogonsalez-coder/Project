import customtkinter as ctk
from app.config import settings

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Система контроля доступа")
        self.geometry("1280x800")
        self._current_mode = None
        self._build_mode_selector()

    def _build_mode_selector(self):
        frame = ctk.CTkFrame(self)
        frame.pack(expand=True)

        ctk.CTkButton(
            frame,
            text="Режим администратора",
            command=self._open_admin,
        ).pack(pady=10)

        ctk.CTkButton(
            frame,
            text="Режим терминала",
            command=self._open_terminal,
        ).pack(pady=10)

    def _open_admin(self):
        from app.gui.admin.admin_view import AdminView
        from app.gui.admin.register_form import RegisterForm
        pwd = ctk.CTkInputDialog(text="Введите пароль:", title="Администратор")
        password = pwd.get_input()
        if password == settings.ADMIN_PASSWORD:
            self._switch_to(AdminView(self))

    def _open_terminal(self):
        from app.gui.terminal.terminal_view import TerminalView
        self._switch_to(TerminalView(self))

    def _switch_to(self, view):
        if self._current_mode:
            self._current_mode.destroy()
        self._current_mode = view
        view.pack(fill="both", expand=True)


def main():
    app = MainWindow()
    app.mainloop()