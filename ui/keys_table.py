import tkinter as tk
from tkinter import ttk
import config
from models import Key, KeyStatus


class KeysTable:
    def __init__(self, parent, delete_callback=None):
        self._frame = tk.Frame(parent, bg=config.BG_COLOR)
        self._delete_callback = delete_callback

        header_frame = tk.Frame(self._frame, bg=config.ACCENT_COLOR)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text="🔑 КЛЮЧИ И КАБИНЕТЫ", 
                 bg=config.ACCENT_COLOR, fg="white", font=config.FONT_SMALL, 
                 padx=10, pady=6).pack(side=tk.LEFT)

        columns = ('cabinet', 'status', 'holder')
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", 
                        background="white",
                        fieldbackground="white", 
                        foreground="#1e293b",
                        rowheight=32,
                        font=config.FONT_NORMAL)
        style.configure("Treeview.Heading",
                        background=config.ACCENT_COLOR,
                        foreground="white",
                        font=("Segoe UI", 10, "bold"),
                        padding=5)
        style.map("Treeview", background=[('selected', config.ACCENT_COLOR)])
        
        self._tree = ttk.Treeview(self._frame, columns=columns, show='headings', height=6)
        self._tree.heading('cabinet', text='Кабинет')
        self._tree.heading('status', text='Статус')
        self._tree.heading('holder', text='Держатель')
        self._tree.column('cabinet', width=80, anchor='center')
        self._tree.column('status', width=100, anchor='center')
        self._tree.column('holder', width=150, anchor='w')
        
        self._tree.tag_configure('available', foreground=config.SUCCESS_COLOR)
        self._tree.tag_configure('issued', foreground=config.WARNING_COLOR)
        
        self._tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self._context_menu = tk.Menu(self._tree, tearoff=0)
        self._context_menu.add_command(label="Удалить", command=self._on_delete_clicked)
        self._tree.bind("<Button-3>", self._show_context_menu)
        self._tree.bind("<Control-Button-1>", self._show_context_menu)

    @property
    def frame(self):
        return self._frame

    def update_keys(self, keys: list[Key]):
        for item in self._tree.get_children():
            self._tree.delete(item)
        for key in keys:
            status_text = key.status.value
            tag = 'issued' if key.status == KeyStatus.ISSUED else 'available'
            self._tree.insert('', tk.END, values=(key.cabinet, status_text, key.holder_display), tags=(tag,))

    def get_selected_cabinet(self) -> str | None:
        selected = self._tree.selection()
        if selected:
            item = self._tree.item(selected[0])
            values = item['values']
            return values[0] if values else None
        return None

    def _show_context_menu(self, event):
        item = self._tree.identify_row(event.y)
        if item:
            self._tree.selection_set(item)
            self._context_menu.post(event.x_root, event.y_root)

    def _on_delete_clicked(self):
        cabinet = self.get_selected_cabinet()
        if cabinet and self._delete_callback:
            self._delete_callback(cabinet)