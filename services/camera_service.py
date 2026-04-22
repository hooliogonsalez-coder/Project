import cv2
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CameraService:
    def __init__(self):
        self._cap: Optional[cv2.VideoCapture] = None
        self._current_index: int = 0

    def get_available_cameras(self, max_tested: int = 5) -> list[str]:
        available = []
        for i in range(max_tested):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(str(i))
                cap.release()
            cv2.waitKey(1)
        if not available:
            available = ["0 (недоступна)"]
        return available

    def init_camera(self, index: int) -> bool:
        if self._cap is not None:
            self._cap.release()
        self._cap = cv2.VideoCapture(index)
        if not self._cap.isOpened():
            logger.error(f"Камера {index} не открывается")
            self._cap = None
            return False
        self._current_index = index
        logger.info(f"Камера {index} подключена")
        return True

    def switch_camera(self, index: int) -> bool:
        index_int = int(index.split()[0])
        if index_int == self._current_index:
            return True
        return self.init_camera(index_int)

    def read_frame(self) -> Optional[cv2.Mat]:
        if self._cap is not None and self._cap.isOpened():
            ret, frame = self._cap.read()
            if ret:
                return frame
        return None

    def is_connected(self) -> bool:
        return self._cap is not None and self._cap.isOpened()

    def release(self):
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    @property
    def current_index(self) -> int:
        return self._current_index
