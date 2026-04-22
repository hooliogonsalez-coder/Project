import tkinter as tk
import config
from models import Employee


class EmployeeCard:
    def __init__(self, parent):
        self._frame = tk.Frame(parent, bg=config.CARD_BG)
        
        header = tk.Label(self._frame, text="👤 ИНФОРМАЦИЯ О СОТРУДНИКЕ",
                          bg=config.ACCENT_COLOR, fg="white", font=config.FONT_SMALL,
                          pady=8, padx=10)
        header.pack(fill=tk.X)

        content = tk.Frame(self._frame, bg=config.CARD_BG, padx=15, pady=12)
        content.pack(fill=tk.X)

        self._avatar_frame = tk.Frame(content, bg=config.CARD_BG)
        self._avatar_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        self._avatar_canvas = tk.Canvas(self._avatar_frame, width=60, height=60, 
                                        bg="white", highlightthickness=0)
        self._avatar_canvas.pack()
        self._avatar_canvas.create_oval(5, 5, 55, 55, fill="#cbd5e1", outline="")
        self._avatar_canvas.create_text(30, 30, text="👤", font=("Segoe UI", 24), fill="white")

        info_frame = tk.Frame(content, bg=config.CARD_BG)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self._name_label = tk.Label(info_frame, text="ФИО: —", bg=config.CARD_BG, 
                                    font=("Segoe UI", 11, "bold"), anchor="w", fg="#1e293b")
        self._name_label.pack(fill=tk.X, pady=2)

        self._position_label = tk.Label(info_frame, text="Должность: —", bg=config.CARD_BG,
                                         font=config.FONT_NORMAL, anchor="w", fg="#64748b")
        self._position_label.pack(fill=tk.X, pady=2)

        self._access_label = tk.Label(info_frame, text="Доступ: —", bg=config.CARD_BG,
                                       font=config.FONT_NORMAL, anchor="w", fg="#64748b")
        self._access_label.pack(fill=tk.X, pady=2)

    @property
    def frame(self):
        return self._frame

    def update_employee(self, employee: Employee | None):
        if employee:
            self._name_label.config(text=f"ФИО: {employee.name}")
            self._position_label.config(text=f"Должность: {employee.position}")
            access_text = "✅ Да" if employee.has_access else "❌ Нет"
            self._access_label.config(text=f"Доступ: {access_text}")
            
            color = config.SUCCESS_COLOR if employee.has_access else config.ERROR_COLOR
            self._access_label.config(fg=color)
            
            self._avatar_canvas.delete("all")
            self._avatar_canvas.create_oval(5, 5, 55, 55, fill=config.ACCENT_COLOR, outline="")
            initials = self._get_initials(employee.name)
            self._avatar_canvas.create_text(30, 30, text=initials, font=("Segoe UI", 18, "bold"), fill="white")
            
            self._animate_highlight()
        else:
            self._name_label.config(text="ФИО: —")
            self._position_label.config(text="Должность: —")
            self._access_label.config(text="Доступ: —", fg="#64748b")
            
            self._avatar_canvas.delete("all")
            self._avatar_canvas.create_oval(5, 5, 55, 55, fill="#cbd5e1", outline="")
            self._avatar_canvas.create_text(30, 30, text="👤", font=("Segoe UI", 24), fill="white")

    def _get_initials(self, name: str) -> str:
        parts = name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        return name[:2].upper() if name else "?"

    def _animate_highlight(self):
        def flash(count=0):
            if count >= 6:
                self._frame.config(bg=config.CARD_BG)
                return
            color = config.ACCENT_COLOR if count % 2 == 0 else config.CARD_BG
            self._frame.config(bg=color)
            self._frame.after(50, lambda: flash(count + 1))
        flash()

    def clear(self):
        self.update_employee(None)