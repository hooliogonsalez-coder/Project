import os
import numpy as np
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class EmbeddingCrypto:
    def __init__(self, key_hex: str):
        self.key = bytes.fromhex(key_hex)
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, embedding: np.ndarray) -> bytes:
        plaintext = embedding.astype(np.float32).tobytes()
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, None)
        return nonce + ciphertext

    def decrypt(self, data: bytes) -> np.ndarray:
        nonce, ciphertext = data[:12], data[12:]
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        return np.frombuffer(plaintext, dtype=np.float32)