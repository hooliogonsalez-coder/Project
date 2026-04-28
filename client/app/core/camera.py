import threading
import queue
import cv2


class CameraThread(threading.Thread):
    def __init__(self, source=0, fps=15):
        super().__init__(daemon=True)
        self.source = source
        self.fps = fps
        self.frame_queue = queue.Queue(maxsize=2)
        self._stop_event = threading.Event()

    def run(self):
        cap = cv2.VideoCapture(self.source)
        cap.set(cv2.CAP_PROP_FPS, self.fps)
        while not self._stop_event.is_set():
            ret, frame = cap.read()
            if ret:
                if self.frame_queue.full():
                    self.frame_queue.get_nowait()
                self.frame_queue.put(frame)
        cap.release()

    def get_frame(self):
        try:
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return None

    def stop(self):
        self._stop_event.set()