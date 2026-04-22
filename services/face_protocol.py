from typing import Protocol


class FaceRecognitionProtocol(Protocol):
    def recognize(self, frame) -> int | None: ...
