import pytest
from httpx import ASGITransport, AsyncClient


def test_l_application_demarre():
    from app.main import app

    assert app.title == "E-commerce Watch API"


@pytest.mark.anyio
async def test_la_racine_repond():
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
