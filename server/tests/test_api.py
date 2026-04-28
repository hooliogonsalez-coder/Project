import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_create_employee():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/employees",
            json={
                "name": "Иван",
                "surname": "Иванов",
                "department": "ИТ",
                "position": "Разработчик",
                "face_embedding_b64": "AQEBAQEB=",
            },
            headers={"X-API-Key": "your-secret-api-key"},
        )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_list_employees():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/employees",
            headers={"X-API-Key": "your-secret-api-key"},
        )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])