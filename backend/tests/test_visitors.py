import uuid

from fastapi.testclient import TestClient

from app.core.security import hash_access_code
from app.models import Visitor


def _register(client: TestClient) -> dict:
    response = client.post(
        "/api/v1/visitors/register",
        json={"name": "  Ada   Lovelace  ", "consent": True},
    )
    assert response.status_code == 201
    return response.json()


def test_register_visitor_returns_access_code_once(client: TestClient):
    registration = _register(client)

    assert registration["name"] == "Ada Lovelace"
    assert len(registration["access_code"].replace("-", "")) == 16
    assert "access_code_hash" not in registration


def test_registration_requires_consent_and_name(client: TestClient):
    no_consent = client.post(
        "/api/v1/visitors/register",
        json={"name": "Ada", "consent": False},
    )
    blank_name = client.post(
        "/api/v1/visitors/register",
        json={"name": "   ", "consent": True},
    )

    assert no_consent.status_code == 422
    assert blank_name.status_code == 422


def test_returning_visitor_can_verify_access_code(client: TestClient):
    registration = _register(client)
    response = client.post(
        "/api/v1/visitors/verify",
        json={"access_code": registration["access_code"].lower()},
    )

    assert response.status_code == 200
    assert response.json()["id"] == registration["id"]
    assert "access_code" not in response.json()
    assert "access_code_hash" not in response.json()


def test_invalid_access_code_is_rejected(client: TestClient):
    response = client.post(
        "/api/v1/visitors/verify",
        json={"access_code": "ZZZZ-ZZZZ-ZZZZ-ZZZZ"},
    )

    assert response.status_code == 401


def test_current_visitor_requires_access_code_header(client: TestClient):
    registration = _register(client)
    response = client.get(
        "/api/v1/visitors/me",
        headers={"X-Visitor-Access-Code": registration["access_code"]},
    )

    assert response.status_code == 200
    assert response.json()["id"] == registration["id"]
    assert client.get("/api/v1/visitors/me").status_code == 422


def test_database_health_check_uses_database_dependency(client: TestClient):
    response = client.get("/health/database")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "database": "connected"}


def test_only_access_code_hash_is_persisted(client: TestClient):
    registration = _register(client)
    with client.app.state.test_session() as db:
        visitor = db.get(Visitor, uuid.UUID(registration["id"]))
        assert visitor is not None
        assert visitor.access_code_hash == hash_access_code(registration["access_code"])
        assert visitor.access_code_hash != registration["access_code"]
