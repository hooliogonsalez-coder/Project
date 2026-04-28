import httpx
from app.config import settings


class APIClient:
    def __init__(self):
        self._client = httpx.Client(
            base_url=settings.SERVER_URL,
            headers={"X-API-Key": settings.API_KEY},
            verify=True,
            timeout=10.0,
        )

    def get_employees(self):
        resp = self._client.get("/api/employees")
        resp.raise_for_status()
        return resp.json()

    def get_rooms(self):
        resp = self._client.get("/api/rooms")
        resp.raise_for_status()
        return resp.json()

    def create_employee(self, data):
        resp = self._client.post("/api/employees", json=data)
        resp.raise_for_status()
        return resp.json()

    def create_room(self, data):
        resp = self._client.post("/api/rooms", json=data)
        resp.raise_for_status()
        return resp.json()

    def sync(self, since: str):
        resp = self._client.post("/api/sync", json={"since": since})
        resp.raise_for_status()
        return resp.json()

    def close(self):
        self._client.close()