import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import config


class VideoPanel:
    def __init__(self, parent):
        self._frame = tk.Frame(parent, bg="#e2e8f0")
        
        header_frame = tk.Frame(self._frame, bg=config.ACCENT_COLOR, height=32)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="📹 Видеопоток", bg=config.ACCENT_COLOR, 
                 fg="white", font=config.FONT_SMALL).pack(side=tk.LEFT, padx=12, pady=6)
        
        self._status_label = tk.Label(header_frame, text="○", bg=config.ACCENT_COLOR, 
                                       fg=config.ERROR_COLOR, font=("Segoe UI", 10))
        self._status_label.pack(side=tk.RIGHT, padx=12)
        
        video_container = tk.Frame(self._frame, bg="#1e293b", padx=4, pady=4)
        video_container.pack(fill=tk.BOTH, expand=True)
        
        self._video_label = tk.Label(video_container, bg="#1e293b", height=config.VIDEO_TARGET_HEIGHT,
                                      text="📷 Камера недоступна", fg="#64748b", font=("Segoe UI", 11))
        self._video_label.pack(fill=tk.BOTH, expand=True)

    @property
    def frame(self):
        return self._frame

    def update_frame(self, cv_frame):
        if cv_frame is None:
            self._status_label.config(text="○", fg=config.ERROR_COLOR)
            if not hasattr(self, '_placeholder_shown'):
                self._video_label.config(text="📷 Камера недоступна")
                self._placeholder_shown = True
            return
        
        self._placeholder_shown = False
        self._status_label.config(text="●", fg=config.SUCCESS_COLOR)
        self._video_label.config(text="")
        
        frame_rgb = cv2.cvtColor(cv_frame, cv2.COLOR_BGR2RGB)
        h, w = frame_rgb.shape[:2]
        target_h = config.VIDEO_TARGET_HEIGHT
        target_w = int(w * target_h / h)
        if target_w <= 0:
            target_w = 320
        frame_resized = cv2.resize(frame_rgb, (target_w, target_h))
        img = Image.fromarray(frame_resized)
        imgtk = ImageTk.PhotoImage(image=img)
        self._video_label.imgtk = imgtk
        self._video_label.config(image=imgtk)