import os

import pytest
from httpx import ASGITransport, AsyncClient

# On injecte de fausses variables d'environnement pour éviter que Pydantic ne râle dans la CI
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("SMTP_HOST", "localhost")
os.environ.setdefault("SMTP_USER", "test")
os.environ.setdefault("SMTP_PASSWORD", "test")
os.environ.setdefault("SMTP_FROM", "test@example.com")
os.environ.setdefault("API_SECRET_KEY", "super-secret-key-pour-les-tests-ci")
os.environ.setdefault("ALERT_RECIPIENT", "admin@example.com")


def test_l_application_demarre():
    from app.main import app

    assert app.title == "E-commerce Watch API"


@pytest.mark.anyio
async def test_la_racine_repond():
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
    # On accepte un 200 ou 404 standard de FastAPI.
    # L'important est que l'application démarre et réponde.
    assert response.status_code in [200, 404]
