import tkinter as tk
from tkinter import ttk
import config


class AddKeyDialog:
    def __init__(self, parent, data_store, callback=None):
        self._parent = parent
        self._store = data_store
        self._callback = callback
        
        self._dialog = tk.Toplevel(parent)
        self._dialog.title("Добавить кабинет")
        self._dialog.geometry("400x200")
        self._dialog.transient(parent)
        self._dialog.grab_set()
        self._dialog.resizable(False, False)
        
        self._setup_ui()

    def _setup_ui(self):
        main_frame = ttk.Frame(self._dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title = tk.Label(main_frame, text="Добавить кабинет", font=config.FONT_TITLE)
        title.pack(pady=(0, 20))
        
        ttk.Label(main_frame, text="Номер кабинета:").pack(anchor=tk.W, pady=(0, 5))
        self._cabinet_entry = ttk.Entry(main_frame, width=40)
        self._cabinet_entry.pack(fill=tk.X, pady=(0, 20))
        
        self._cabinet_entry.focus()
        self._dialog.bind("<Return>", lambda e: self._save())
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        self._left_placeholder = ttk.Label(btn_frame, text="")
        self._left_placeholder.grid(row=0, column=0, padx=2, sticky="ew")
        
        cancel_btn = ttk.Button(btn_frame, text="Отмена", command=self._on_close)
        cancel_btn.grid(row=0, column=1, padx=2, sticky="ew")
        
        save_btn = ttk.Button(btn_frame, text="Сохранить", command=self._save)
        save_btn.grid(row=0, column=2, padx=2, sticky="ew")
        
        self._right_placeholder = ttk.Label(btn_frame, text="")
        self._right_placeholder.grid(row=0, column=3, padx=2, sticky="ew")
        
        btn_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self._dialog.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        self._dialog.destroy()

    def _save(self):
        cabinet = self._cabinet_entry.get().strip()
        
        if not cabinet:
            tk.messagebox.showerror("Ошибка", "Введите номер кабинета", parent=self._dialog)
            return
        
        existing = self._store.get_key(cabinet)
        if existing:
            tk.messagebox.showerror("Ошибка", f"Кабинет {cabinet} уже существует", parent=self._dialog)
            return
        
        self._store.add_key(cabinet)
        
        tk.messagebox.showinfo("Успех", f"Кабинет {cabinet} добавлен", parent=self._dialog)
        if self._callback:
            self._callback(cabinet)
        self._on_close()