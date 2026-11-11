from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.core.config import settings
from app.core.security import hash_admin_password
from app.models.admin_user import AdminUser


ADMIN_USERNAME = "memory-admin"
ADMIN_PASSWORD = "secure-test-password-2026"
ADMIN_TOKEN_SECRET = "test-only-admin-signing-secret-32-bytes"


def _login(client: TestClient, monkeypatch) -> str:
    monkeypatch.setattr(settings, "admin_token_secret", ADMIN_TOKEN_SECRET)
    with client.app.state.test_session() as db:
        db.add(
            AdminUser(
                username=ADMIN_USERNAME,
                password_hash=hash_admin_password(ADMIN_PASSWORD),
            )
        )
        db.commit()
    response = client.post(
        "/api/v1/admin/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def _register(client: TestClient) -> dict:
    response = client.post(
        "/api/v1/visitors/register",
        json={"name": "Admin managed visitor", "consent": True},
    )
    assert response.status_code == 201
    return response.json()


def _image_bytes() -> bytes:
    image = Image.new("RGB", (4, 3), color=(30, 120, 200))
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def test_admin_login_and_protected_dashboard(client: TestClient, monkeypatch):
    token = _login(client, monkeypatch)
    headers = {"Authorization": f"Bearer {token}"}

    dashboard = client.get("/api/v1/admin/dashboard", headers=headers)
    unauthorized = client.get("/api/v1/admin/dashboard")
    tampered = client.get(
        "/api/v1/admin/dashboard",
        headers={"Authorization": f"Bearer {token}x"},
    )

    assert dashboard.status_code == 200
    assert dashboard.json() == {
        "total_visitors": 0,
        "active_visitors": 0,
        "total_photos": 0,
    }
    assert unauthorized.status_code == 401
    assert tampered.status_code == 401


def test_admin_can_disable_and_reactivate_visitor(client: TestClient, monkeypatch):
    token = _login(client, monkeypatch)
    visitor = _register(client)
    headers = {"Authorization": f"Bearer {token}"}
    visitor_headers = {"X-Visitor-Access-Code": visitor["access_code"]}

    disabled = client.patch(
        f"/api/v1/admin/visitors/{visitor['id']}",
        headers=headers,
        json={"is_active": False},
    )
    visitor_access = client.get(
        "/api/v1/visitors/me", headers=visitor_headers
    )
    disabled_feed = client.get(
        "/api/v1/slideshow/photos", headers=visitor_headers
    )
    reactivated = client.patch(
        f"/api/v1/admin/visitors/{visitor['id']}",
        headers=headers,
        json={"is_active": True},
    )
    restored_access = client.get(
        "/api/v1/visitors/me", headers=visitor_headers
    )

    assert disabled.status_code == 200
    assert disabled.json()["is_active"] is False
    assert visitor_access.status_code == 401
    assert disabled_feed.status_code == 401
    assert reactivated.status_code == 200
    assert reactivated.json()["is_active"] is True
    assert restored_access.status_code == 200


def test_admin_can_delete_photos_and_update_slideshow_defaults(
    client: TestClient, monkeypatch, tmp_path
):
    monkeypatch.setattr(settings, "storage_path", tmp_path)
    token = _login(client, monkeypatch)
    visitor = _register(client)
    upload_response = client.post(
        "/api/v1/photos/upload",
        headers={"X-Visitor-Access-Code": visitor["access_code"]},
        files=[("files", ("memory.jpg", _image_bytes(), "image/jpeg"))],
    )
    assert upload_response.status_code == 201
    photo_id = upload_response.json()[0]["id"]
    headers = {"Authorization": f"Bearer {token}"}

    photo_list = client.get("/api/v1/admin/photos", headers=headers)
    visitor_photo_list = client.get(
        f"/api/v1/admin/photos?visitor_id={visitor['id']}",
        headers=headers,
    )
    settings_response = client.put(
        "/api/v1/admin/settings",
        headers=headers,
        json={
            "slide_duration_seconds": 12,
            "refresh_interval_seconds": 10,
            "fade_duration_ms": 1000,
            "allow_shuffle": False,
            "allow_fullscreen": True,
        },
    )
    delete_response = client.delete(
        f"/api/v1/admin/photos/{photo_id}", headers=headers
    )
    visitor_feed = client.get(
        "/api/v1/slideshow/photos",
        headers={"X-Visitor-Access-Code": visitor["access_code"]},
    )

    assert photo_list.status_code == 200
    assert len(visitor_photo_list.json()) == 1
    assert photo_list.json()[0]["visitor_name"] == "Admin managed visitor"
    assert settings_response.status_code == 200
    assert settings_response.json()["slide_duration_seconds"] == 12
    assert settings_response.json()["allow_shuffle"] is False
    public_settings = client.get("/api/v1/slideshow/settings")
    assert public_settings.json()["slide_duration_seconds"] == 12
    assert delete_response.status_code == 204
    assert visitor_feed.json() == []
