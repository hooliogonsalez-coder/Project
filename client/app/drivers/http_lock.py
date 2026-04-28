import httpx
from app.core.lock_driver import LockDriver


class HttpLockDriver(LockDriver):
    def __init__(self, base_url: str, api_key: str, open_duration_sec: int = 5):
        self._client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5.0,
        )
        self._duration = open_duration_sec

    def open(self, room_id: str) -> bool:
        try:
            resp = self._client.post(
                f"/lock/{room_id}/open",
                json={"duration": self._duration},
            )
            return resp.status_code == 200
        except Exception:
            return False

    def close(self, room_id: str) -> bool:
        try:
            resp = self._client.post(f"/lock/{room_id}/close")
            return resp.status_code == 200
        except Exception:
            return False

    def status(self, room_id: str) -> str:
        try:
            resp = self._client.get(f"/lock/{room_id}/status")
            return resp.json().get("state", "error")
        except Exception:
            return "error"