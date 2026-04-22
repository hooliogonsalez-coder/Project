import logging
import numpy as np
import cv2
import os
import shutil
from pathlib import Path
from typing import Optional, Union, Tuple

from core.interfaces import FaceRecognizer, EmployeeRepository
from models import Employee

logger = logging.getLogger(__name__)

FD_MODEL_PATH = os.path.join(os.path.expanduser('~'), '.mediapipe', 'models', 'blaze_face_short_range.tflite')
ARCFACE_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'arcface_w600k_r50.onnx')


class FaceService(FaceRecognizer):
    def __init__(self, employee_repo: EmployeeRepository, threshold: float = None):
        import config
        self._employee_repo = employee_repo
        self._threshold = threshold or config.FACE_THRESHOLD
        self._photos_dir = config.PHOTOS_DIR
        self._current_employee: Optional[Employee] = None
        self._face_detector = None
        self._arcface = None
        self._arcface_inp = None
        self._arcface_out = None
        self._mp_face_detector = None
        self._init_models()

    def _init_models(self):
        if not os.path.exists(FD_MODEL_PATH):
            logger.warning(f"FaceDetector model not found at {FD_MODEL_PATH}")
            return
        if not os.path.exists(ARCFACE_MODEL_PATH):
            logger.warning(f"ArcFace model not found at {ARCFACE_MODEL_PATH}")
            return

        try:
            from mediapipe.tasks.python import BaseOptions
            from mediapipe.tasks.python.vision import FaceDetector, FaceDetectorOptions, RunningMode
            import mediapipe as mp

            options = FaceDetectorOptions(
                base_options=BaseOptions(model_asset_path=FD_MODEL_PATH),
                running_mode=RunningMode.IMAGE
            )
            self._face_detector = FaceDetector.create_from_options(options)
            self._mp_image = mp.Image
            self._mp_image_format = mp.ImageFormat.SRGB
            logger.info("FaceDetector model loaded")

            import onnxruntime as ort
            sess_opts = ort.SessionOptions()
            sess_opts.inter_op_num_threads = 1
            self._arcface = ort.InferenceSession(
                ARCFACE_MODEL_PATH,
                sess_opts=sess_opts,
                providers=['CPUExecutionProvider']
            )
            self._arcface_inp = self._arcface.get_inputs()[0].name
            self._arcface_out = self._arcface.get_outputs()[0].name
            logger.info("ArcFace model loaded")
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            self._face_detector = None
            self._arcface = None

    def _init_photos_dir(self):
        Path(self._photos_dir).mkdir(parents=True, exist_ok=True)

    def _preprocess_image(self, image_rgb: np.ndarray) -> np.ndarray:
        h, w = image_rgb.shape[:2]
        if h < 200 or w < 200:
            scale = max(200 / h, 200 / w)
            new_w, new_h = int(w * scale), int(h * scale)
            image_rgb = cv2.resize(image_rgb, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        return image_rgb

    def _detect_face(self, image_rgb: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        if self._face_detector is None:
            return None

        img_uint8 = image_rgb.astype(np.uint8)
        mp_img = self._mp_image(
            image_format=self._mp_image_format.SRGB,
            data=img_uint8
        )
        result = self._face_detector.detect(mp_img)

        if not result.detections:
            return None

        det = result.detections[0]
        bbox = det.bounding_box
        x1 = int(bbox.origin_x)
        y1 = int(bbox.origin_y)
        x2 = int(x1 + bbox.width)
        y2 = int(y1 + bbox.height)

        h, w = image_rgb.shape[:2]
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)

        if x2 <= x1 or y2 <= y1:
            return None
        return (x1, y1, x2, y2)

    def _crop_and_preprocess_face(self, image_rgb: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        x1, y1, x2, y2 = bbox
        face = image_rgb[y1:y2, x1:x2]
        if face.size == 0:
            return None

        h_img, w_img = image_rgb.shape[:2]
        face_w, face_h = x2 - x1, y2 - y1
        face_ratio = (face_w * face_h) / (w_img * h_img)
        if face_ratio < 0.015:
            logger.warning(f"Face too small: ratio={face_ratio:.4f}")
            return None

        resized = cv2.resize(face, (112, 112), interpolation=cv2.INTER_AREA)
        mean = np.array([127.5, 127.5, 127.5], dtype=np.float32)
        std = np.array([127.5, 127.5, 127.5], dtype=np.float32)
        normalized = (resized.astype(np.float32) - mean) / std
        blob = normalized.transpose(2, 0, 1).astype(np.float32)
        return blob[np.newaxis]

    def _encode_image(self, image_rgb: np.ndarray) -> Optional[np.ndarray]:
        bbox = self._detect_face(image_rgb)
        if bbox is None:
            return None

        blob = self._crop_and_preprocess_face(image_rgb, bbox)
        if blob is None:
            return None

        embedding = self._arcface.run([self._arcface_out], {self._arcface_inp: blob})[0]
        embedding = embedding.flatten()
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding

    def encode_face(self, image_source: Union[str, bytes]) -> Optional[bytes]:
        try:
            from PIL import Image
            import io

            if isinstance(image_source, str):
                image = Image.open(image_source)
            else:
                image = Image.open(io.BytesIO(image_source))

            image_array = np.array(image)

            if len(image_array.shape) == 2:
                image_rgb = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
            elif image_array.shape[2] == 4:
                image_rgb = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
            else:
                image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)

            image_rgb = self._preprocess_image(image_rgb)
            embedding = self._encode_image(image_rgb)
            if embedding is not None:
                return embedding.tobytes()
            return None
        except Exception as e:
            logger.error(f"Ошибка кодирования лица: {e}")
            return None

    def _save_photo(self, source_path: str, emp_id: int, full_name: str) -> str:
        ext = os.path.splitext(source_path)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png']:
            ext = '.jpg'

        safe_name = "".join(c for c in full_name if c.isalnum() or c in ' -_').strip()
        safe_name = safe_name.replace(' ', '_')

        filename = f"{emp_id}_{safe_name}{ext}"
        dest_path = os.path.join(self._photos_dir, filename)

        shutil.copy2(source_path, dest_path)
        return dest_path

    def encode(self, image_source: bytes) -> Optional[bytes]:
        return self.encode_face(image_source)

    def recognize(self, frame) -> Optional[Employee]:
        try:
            from PIL import Image
            import io

            if isinstance(frame, bytes):
                image = Image.open(io.BytesIO(frame))
                image_array = np.array(image)
            else:
                image_array = frame

            if len(image_array.shape) == 2:
                image_rgb = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
            elif image_array.shape[2] == 4:
                image_rgb = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
            elif image_array.shape[2] == 3:
                image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image_array

            embedding = self._encode_image(image_rgb)
            if embedding is None:
                logger.warning("Лицо не обнаружено на кадре")
                return None

            face_encoding_bytes = embedding.tobytes()
            employee = self._employee_repo.find_by_face(face_encoding_bytes, self._threshold)

            if employee:
                self._current_employee = employee
                logger.info(f"Распознан: {employee.name}")
            return employee
        except Exception as e:
            logger.error(f"Ошибка распознавания лица: {e}")
            return None

    def add_employee(self, full_name: str, position: str, photo_path: str) -> Optional[int]:
        face_encoding = self.encode_face(photo_path)
        if face_encoding is None:
            logger.error("Не удалось получить эмбеддинг лица из фото. Попробуйте фото с хорошим освещением и лицом крупным планом.")
            return None

        temp_id = 0
        photo_saved_path = self._save_photo(photo_path, temp_id, full_name)

        emp_id = self._employee_repo.add(full_name, position, face_encoding, photo_saved_path)

        if emp_id:
            final_photo_path = self._save_photo(photo_path, emp_id, full_name)
            self._employee_repo.update(emp_id, photo_path=final_photo_path)

        logger.info(f"Добавлен сотрудник: {full_name} (ID: {emp_id})")
        return emp_id

    def set_employee(self, emp: Employee):
        self._current_employee = emp

    def clear_employee(self):
        self._current_employee = None

    @property
    def current_employee(self) -> Optional[Employee]:
        return self._current_employee

    def validate_photo(self, photo_path: str) -> Tuple[bool, str]:
        try:
            from PIL import Image
            image = Image.open(photo_path)
            image_array = np.array(image)

            if len(image_array.shape) == 2:
                image_rgb = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
            elif image_array.shape[2] == 4:
                image_rgb = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
            else:
                image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)

            bbox = self._detect_face(image_rgb)
            if bbox is None:
                return False, "Лицо не обнаружено"

            x1, y1, x2, y2 = bbox
            h, w = image_rgb.shape[:2]
            face_ratio = ((x2 - x1) * (y2 - y1)) / (w * h)
            if face_ratio < 0.015:
                return False, "Лицо слишком маленькое на фото"
            if face_ratio < 0.04:
                return True, "Лицо маловато, но пойдёт"
            return True, ""
        except Exception as e:
            return False, f"Ошибка чтения фото: {e}"