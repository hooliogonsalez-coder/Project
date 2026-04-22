import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import os
import config


class AddEmployeeDialog:
    def __init__(self, parent, face_service, camera_service, callback=None):
        self._parent = parent
        self._face_service = face_service
        self._camera_service = camera_service
        self._callback = callback
        self._photo_path = None
        self._photo_tk = None
        self._is_camera_mode = False
        self._camera_preview_tk = None
        
        self._dialog = tk.Toplevel(parent)
        self._dialog.title("Добавить сотрудника")
        self._dialog.geometry("400x500")
        self._dialog.transient(parent)
        self._dialog.grab_set()
        self._dialog.resizable(False, False)
        
        self._setup_ui()

    def _setup_ui(self):
        main_frame = ttk.Frame(self._dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title = tk.Label(main_frame, text="Добавление сотрудника", font=config.FONT_TITLE)
        title.pack(pady=(0, 20))
        
        ttk.Label(main_frame, text="ФИО:").pack(anchor=tk.W, pady=(0, 5))
        self._name_entry = ttk.Entry(main_frame, width=40)
        self._name_entry.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(main_frame, text="Должность:").pack(anchor=tk.W, pady=(0, 5))
        self._position_entry = ttk.Entry(main_frame, width=40)
        self._position_entry.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(main_frame, text="Фото:").pack(anchor=tk.W, pady=(0, 5))
        
        photo_frame = ttk.Frame(main_frame)
        photo_frame.pack(fill=tk.X, pady=(0, 20))
        
        self._select_photo_btn = ttk.Button(photo_frame, text="Выбрать фото", 
                                           command=self._select_photo)
        self._select_photo_btn.pack(side=tk.LEFT)
        
        self._take_photo_btn = ttk.Button(photo_frame, text="Сделать фото", 
                                         command=self._start_camera_mode)
        self._take_photo_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        self._photo_label = tk.Label(photo_frame, text="Фото не выбрано", 
                                     fg="gray", font=config.FONT_SMALL)
        self._photo_label.pack(side=tk.LEFT, padx=(10, 0))
        
        self._preview_frame = ttk.Frame(main_frame, width=150, height=150)
        self._preview_frame.pack(pady=(0, 20))
        self._preview_frame.pack_propagate(False)
        
        self._preview_label = tk.Label(self._preview_frame, bg="white", text="Превью")
        self._preview_label.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)

        self._left_placeholder = ttk.Label(btn_frame, text="")
        self._left_placeholder.grid(row=0, column=0, padx=2, sticky="ew")

        self._cancel_btn = ttk.Button(btn_frame, text="Отмена", command=self._on_close)
        self._cancel_btn.grid(row=0, column=1, padx=2, sticky="ew")

        self._save_btn = ttk.Button(btn_frame, text="Сохранить", command=self._save)
        self._save_btn.grid(row=0, column=2, padx=2, sticky="ew")

        self._right_placeholder = ttk.Label(btn_frame, text="")
        self._right_placeholder.grid(row=0, column=3, padx=2, sticky="ew")

        self._capture_btn = ttk.Button(btn_frame, text="Снять", command=self._capture_photo)
        self._capture_btn.grid(row=0, column=2, padx=2, sticky="ew")
        self._capture_btn.grid_remove()

        self._cancel_capture_btn = ttk.Button(btn_frame, text="Отмена", command=self._cancel_camera_mode)
        self._cancel_capture_btn.grid(row=0, column=1, padx=2, sticky="ew")
        self._cancel_capture_btn.grid_remove()

        btn_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._dialog.protocol("WM_DELETE_WINDOW", self._on_close)

    def _select_photo(self):
        filename = filedialog.askopenfilename(
            title="Выберите фото",
            filetypes=[
                ("Изображения", "*.jpg *.jpeg *.png *.bmp"),
                ("Все файлы", "*.*")
            ]
        )
        
        if filename:
            self._photo_path = filename
            self._photo_label.config(text=os.path.basename(filename))
            self._update_preview()

    def _start_camera_mode(self):
        if self._camera_service is None:
            tk.messagebox.showerror("Ошибка", "Камера недоступна", parent=self._dialog)
            return
        
        self._is_camera_mode = True
        self._photo_label.config(text="Режим камеры...")
        self._select_photo_btn.config(state="disabled")
        self._take_photo_btn.config(state="disabled")
        
        self._left_placeholder.grid_remove()
        self._right_placeholder.grid_remove()
        self._cancel_btn.grid_remove()
        self._save_btn.grid_remove()
        
        self._capture_btn.grid()
        self._cancel_capture_btn.grid()
        
        self._update_camera_preview()

    def _update_camera_preview(self):
        if not self._is_camera_mode:
            return
        
        frame = self._camera_service.read_frame()
        
        if frame is not None:
            try:
                from PIL import Image
                import numpy as np
                import cv2
                
                if len(frame.shape) == 3 and frame.shape[2] == 3:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                else:
                    frame_rgb = frame
                
                img = Image.fromarray(frame_rgb)
                img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                self._camera_preview_tk = ImageTk.PhotoImage(img)
                self._preview_label.config(image=self._camera_preview_tk, text="")
            except Exception as e:
                self._preview_label.config(text="Ошибка камеры")
        
        if self._is_camera_mode:
            self._dialog.after(30, self._update_camera_preview)

    def _capture_photo(self):
        frame = self._camera_service.read_frame()
        
        if frame is None:
            tk.messagebox.showerror("Ошибка", "Не удалось сделать снимок", parent=self._dialog)
            return
        
        import cv2
        import tempfile
        import numpy as np
        
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            frame_rgb = frame
        
        temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        cv2.imwrite(temp_file.name, cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR))
        
        self._photo_path = temp_file.name
        self._photo_label.config(text="Фото с камеры")
        
        self._stop_camera_mode()
        self._update_preview()

    def _cancel_camera_mode(self):
        self._stop_camera_mode()
        self._photo_label.config(text="Фото не выбрано")
        self._preview_label.config(image="", text="Превью")

    def _stop_camera_mode(self):
        self._is_camera_mode = False
        self._select_photo_btn.config(state="normal")
        self._take_photo_btn.config(state="normal")
        
        self._capture_btn.grid_remove()
        self._cancel_capture_btn.grid_remove()
        
        self._left_placeholder.grid()
        self._right_placeholder.grid()
        self._cancel_btn.grid()
        self._save_btn.grid()

    def _update_preview(self):
        if not self._photo_path or not os.path.exists(self._photo_path):
            return
        
        try:
            img = Image.open(self._photo_path)
            img.thumbnail((150, 150), Image.Resampling.LANCZOS)
            self._photo_tk = ImageTk.PhotoImage(img)
            self._preview_label.config(image=self._photo_tk, text="")
        except Exception as e:
            self._preview_label.config(text="Ошибка загрузки")

    def _on_close(self):
        self._is_camera_mode = False
        self._dialog.destroy()

    def _save(self):
        name = self._name_entry.get().strip()
        position = self._position_entry.get().strip()
        
        if not name:
            tk.messagebox.showerror("Ошибка", "Введите ФИО", parent=self._dialog)
            return
        
        if not position:
            tk.messagebox.showerror("Ошибка", "Введите должность", parent=self._dialog)
            return
        
        if not self._photo_path:
            tk.messagebox.showerror("Ошибка", "Выберите фото", parent=self._dialog)
            return
        
        valid, msg = self._face_service.validate_photo(self._photo_path)
        if not valid:
            tk.messagebox.showerror("Ошибка", f"На фото не обнаружено лицо.\n{msg}\n\nПопробуйте:\n• Фото при хорошем освещении\n• Лицо крупным планом\n• Лицо прямо facing камеру", 
                           parent=self._dialog)
            return
        
        emp_id = self._face_service.add_employee(name, position, self._photo_path)
        
        if emp_id:
            tk.messagebox.showinfo("Успех", f"Сотрудник добавлен (ID: {emp_id})", parent=self._dialog)
            if self._callback:
                self._callback(emp_id, name, position)
            self._on_close()
        else:
            tk.messagebox.showerror("Ошибка", "Не удалось добавить сотрудника.\nПопробуйте другое фото.", 
                                   parent=self._dialog)
