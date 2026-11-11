from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.core.config import settings


def _image_bytes() -> bytes:
    image = Image.new("RGB", (4, 3), color=(30, 120, 200))
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def _register(client: TestClient) -> dict:
    response = client.post(
        "/api/v1/visitors/register",
        json={"name": "Slideshow visitor", "consent": True},
    )
    assert response.status_code == 201
    return response.json()


def _upload(client: TestClient, access_code: str, image: bytes):
    return client.post(
        "/api/v1/photos/upload",
        headers={"X-Visitor-Access-Code": access_code},
        files=[("files", ("memory.jpg", image, "image/jpeg"))],
    )


def test_new_upload_is_immediately_available_in_visitor_slideshow(
    client: TestClient, tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "storage_path", tmp_path)
    visitor = _register(client)
    upload_response = _upload(client, visitor["access_code"], _image_bytes())
    assert upload_response.status_code == 201
    uploaded_photo = upload_response.json()[0]

    slideshow_response = client.get(
        "/api/v1/slideshow/photos",
        headers={"X-Visitor-Access-Code": visitor["access_code"]},
    )

    assert slideshow_response.status_code == 200
    assert slideshow_response.json() == [
        {
            "id": uploaded_photo["id"],
            "original_filename": "memory.jpg",
            "content_type": "image/jpeg",
            "image_url": (
                f"/api/v1/slideshow/photos/{uploaded_photo['id']}/image"
            ),
            "created_at": uploaded_photo["created_at"],
        }
    ]


def test_slideshow_image_endpoint_serves_uploaded_image(
    client: TestClient, tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "storage_path", tmp_path)
    visitor = _register(client)
    original_image = _image_bytes()
    uploaded_photo = _upload(client, visitor["access_code"], original_image).json()[0]

    image_response = client.get(
        f"/api/v1/slideshow/photos/{uploaded_photo['id']}/image",
        headers={"X-Visitor-Access-Code": visitor["access_code"]},
    )

    assert image_response.status_code == 200
    assert image_response.headers["content-type"] == "image/jpeg"
    assert image_response.headers["x-content-type-options"] == "nosniff"
    assert image_response.headers["cache-control"] == "private, no-store"
    assert image_response.content == original_image


def test_slideshow_only_lists_and_serves_current_visitors_photos(
    client: TestClient, tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "storage_path", tmp_path)
    first_visitor = _register(client)
    second_visitor = _register(client)
    first_photo = _upload(
        client, first_visitor["access_code"], _image_bytes()
    ).json()[0]
    second_photo = _upload(
        client, second_visitor["access_code"], _image_bytes()
    ).json()[0]

    first_feed = client.get(
        "/api/v1/slideshow/photos",
        headers={"X-Visitor-Access-Code": first_visitor["access_code"]},
    )
    second_feed = client.get(
        "/api/v1/slideshow/photos",
        headers={"X-Visitor-Access-Code": second_visitor["access_code"]},
    )
    other_visitor_image = client.get(
        f"/api/v1/slideshow/photos/{second_photo['id']}/image",
        headers={"X-Visitor-Access-Code": first_visitor["access_code"]},
    )

    assert [photo["id"] for photo in first_feed.json()] == [first_photo["id"]]
    assert [photo["id"] for photo in second_feed.json()] == [second_photo["id"]]
    assert other_visitor_image.status_code == 404


def test_deleted_photo_disappears_from_owner_slideshow_and_image_endpoint(
    client: TestClient, tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "storage_path", tmp_path)
    visitor = _register(client)
    uploaded_photo = _upload(
        client, visitor["access_code"], _image_bytes()
    ).json()[0]
    headers = {"X-Visitor-Access-Code": visitor["access_code"]}

    delete_response = client.delete(
        f"/api/v1/photos/{uploaded_photo['id']}",
        headers=headers,
    )
    feed_response = client.get("/api/v1/slideshow/photos", headers=headers)
    image_response = client.get(
        f"/api/v1/slideshow/photos/{uploaded_photo['id']}/image",
        headers=headers,
    )

    assert delete_response.status_code == 204
    assert feed_response.json() == []
    assert image_response.status_code == 404


def test_slideshow_photo_endpoints_require_visitor_authentication(
    client: TestClient,
):
    response = client.get("/api/v1/slideshow/photos")

    assert response.status_code == 422


def test_slideshow_settings_provide_playback_intervals(client: TestClient):
    response = client.get("/api/v1/slideshow/settings")

    assert response.status_code == 200
    assert response.json() == {
        "slide_duration_seconds": 7,
        "refresh_interval_seconds": 5,
        "fade_duration_ms": 750,
        "allow_shuffle": True,
        "allow_fullscreen": True,
    }


def test_upload_broadcasts_live_update_to_slideshow_clients(
    client: TestClient, tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "storage_path", tmp_path)
    with client.websocket_connect("/api/v1/slideshow/ws") as websocket:
        visitor = _register(client)
        upload_response = _upload(
            client, visitor["access_code"], _image_bytes()
        )

        assert upload_response.status_code == 201
        assert websocket.receive_json() == {"type": "photos_updated"}
        photo_id = upload_response.json()[0]["id"]
        delete_response = client.delete(
            f"/api/v1/photos/{photo_id}",
            headers={"X-Visitor-Access-Code": visitor["access_code"]},
        )

        assert delete_response.status_code == 204
        assert websocket.receive_json() == {"type": "photos_updated"}


def test_missing_slideshow_image_returns_not_found(client: TestClient):
    visitor = _register(client)
    response = client.get(
        "/api/v1/slideshow/photos/00000000-0000-0000-0000-000000000001/image",
        headers={"X-Visitor-Access-Code": visitor["access_code"]},
    )

    assert response.status_code == 404
