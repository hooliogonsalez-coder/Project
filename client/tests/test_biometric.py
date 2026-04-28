import pytest
import numpy as np
from app.core.biometric import FaceRecognizer


def test_identify_known_employee():
    recognizer = FaceRecognizer(threshold=0.50)
    vec = np.random.rand(512).astype(np.float32)
    vec /= np.linalg.norm(vec)
    recognizer._embeddings = [(42, vec)]

    noisy = vec + np.random.normal(0, 0.05, 512)
    noisy /= np.linalg.norm(noisy)

    assert recognizer.identify(noisy) == 42


def test_reject_unknown():
    recognizer = FaceRecognizer(threshold=0.50)
    vec1 = np.random.rand(512).astype(np.float32)
    vec1 /= np.linalg.norm(vec1)
    vec2 = np.random.rand(512).astype(np.float32)
    vec2 /= np.linalg.norm(vec2)
    recognizer._embeddings = [(1, vec1)]
    assert recognizer.identify(vec2) is None


if __name__ == "__main__":
    test_identify_known_employee()
    test_reject_unknown()
    print("All tests passed!")