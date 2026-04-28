import numpy as np


class FaceRecognizer:
    def __init__(self, model_name="buffalo_l", threshold=0.50):
        self.app = None
        self.model_name = model_name
        self.threshold = threshold
        self._embeddings: list[tuple[int, np.ndarray]] = []

    def load_from_db(self, employees: list[dict]):
        self._embeddings = []
        for emp in employees:
            raw = emp["face_embedding"]
            vec = np.frombuffer(raw, dtype=np.float32)
            self._embeddings.append((emp["id"], vec))

    def detect_and_embed(self, frame: np.ndarray) -> np.ndarray | None:
        if self.app is None:
            return None
        faces = self.app.get(frame)
        if not faces:
            return None
        face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
        return face.normed_embedding

    def identify(self, embedding: np.ndarray) -> int | None:
        if not self._embeddings:
            return None
        ids, vecs = zip(*self._embeddings)
        matrix = np.stack(vecs)
        scores = matrix @ embedding
        best_idx = int(np.argmax(scores))
        if scores[best_idx] >= self.threshold:
            return ids[best_idx]
        return None

    def capture_template(self, frames: list[np.ndarray]) -> np.ndarray | None:
        embeddings = []
        for frame in frames:
            emb = self.detect_and_embed(frame)
            if emb is not None:
                embeddings.append(emb)
        if len(embeddings) < 3:
            return None
        mean_emb = np.mean(embeddings, axis=0)
        return mean_emb / np.linalg.norm(mean_emb)

    def check_liveness(self, frame: np.ndarray, face) -> bool:
        if hasattr(face, "det_score") and face.det_score < 0.85:
            return False
        try:
            spoof_score = face.spoof_score if hasattr(face, "spoof_score") else 1.0
            return spoof_score > 0.5
        except Exception:
            return True