from app.core.lock_driver import LockDriver


class DummyLockDriver(LockDriver):
    def open(self, room_id: str) -> bool:
        print(f"[DUMMY] Opening lock for room {room_id}")
        return True

    def close(self, room_id: str) -> bool:
        print(f"[DUMMY] Closing lock for room {room_id}")
        return True

    def status(self, room_id: str) -> str:
        return "open"