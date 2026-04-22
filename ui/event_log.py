import tkinter as tk
from datetime import datetime
import config


class EventLog:
    def __init__(self, parent):
        self._frame = tk.Frame(parent)

        header_frame = tk.Frame(self._frame, bg=config.ACCENT_COLOR)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text="📋 ЖУРНАЛ СОБЫТИЙ", 
                 bg=config.ACCENT_COLOR, fg="white", font=config.FONT_SMALL, 
                 padx=10, pady=5).pack(side=tk.LEFT)

        self._text = tk.Text(self._frame, wrap=tk.WORD, font=config.FONT_SMALL, 
                             bg="white", fg="#334155", bd=0, highlightthickness=0,
                             padx=10, pady=8)
        self._text.pack(fill=tk.BOTH, expand=True)
        
        self._text.tag_config("success", foreground=config.SUCCESS_COLOR)
        self._text.tag_config("error", foreground=config.ERROR_COLOR)
        self._text.tag_config("info", foreground=config.ACCENT_COLOR)
        self._text.tag_config("warning", foreground=config.WARNING_COLOR)

    @property
    def frame(self):
        return self._frame

    def log(self, message: str, level: str = "info"):
        timestamp = datetime.now().strftime(config.LOG_TIMESTAMP_FORMAT)
        tag = level if level in ("success", "error", "info", "warning") else "info"
        self._text.insert(tk.END, f"[{timestamp}] ", tag)
        self._text.insert(tk.END, f"{message}\n", tag)
        self._text.see(tk.END)

    def clear(self):
        self._text.delete("1.0", tk.END)
