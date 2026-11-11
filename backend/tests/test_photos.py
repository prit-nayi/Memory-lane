from io import BytesIO
import uuid

from fastapi.testclient import TestClient
from PIL import Image

from app.core.config import settings
from app.models import Photo


def _register(client: TestClient, name: str = "Photo Owner") -> dict:
    response = client.post(
        "/api/v1/visitors/register",
        json={"name": name, "consent": True},
    )
    assert response.status_code == 201
    return response.json()


def _image_bytes(image_format: str = "JPEG") -> bytes:
    image = Image.new("RGB", (4, 3), color=(30, 120, 200))
    buffer = BytesIO()
    image.save(buffer, format=image_format)
    return buffer.getvalue()


def _upload(
    client: TestClient,
    access_code: str,
    files: list[tuple[str, tuple[str, bytes, str]]],
):
    return client.post(
        "/api/v1/photos/upload",
        headers={"X-Visitor-Access-Code": access_code},
        files=files,
    )


def test_upload_multiple_valid_images_and_list_metadata(
    client: TestClient, tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "storage_path", tmp_path)
    visitor = _register(client)
    response = _upload(
        client,
        visitor["access_code"],
        [
            ("files", ("first.png", _image_bytes(), "image/png")),
            ("files", ("second.png", _image_bytes("PNG"), "image/png")),
        ],
    )

    assert response.status_code == 201
    uploaded = response.json()
    assert len(uploaded) == 2
    assert {photo["status"] for photo in uploaded} == {"pending"}
    assert {photo["content_type"] for photo in uploaded} == {
        "image/jpeg",
        "image/png",
    }
    assert {
        photo["original_filename"]: photo["content_type"] for photo in uploaded
    } == {"first.png": "image/jpeg", "second.png": "image/png"}
    assert all(photo["visitor_id"] == visitor["id"] for photo in uploaded)
    assert all("storage_key" not in photo for photo in uploaded)
    stored_files = [path for path in tmp_path.iterdir() if path.is_file()]
    assert len(stored_files) == 2
    assert all(path.name.startswith(".") is False for path in stored_files)

    listed = client.get(
        "/api/v1/photos/my-photos",
        headers={"X-Visitor-Access-Code": visitor["access_code"]},
    )
    assert listed.status_code == 200
    assert {photo["id"] for photo in listed.json()} == {
        photo["id"] for photo in uploaded
    }


def test_invalid_image_is_rejected_without_saving_partial_upload(
    client: TestClient, tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "storage_path", tmp_path)
    visitor = _register(client)
    response = _upload(
        client,
        visitor["access_code"],
        [
            ("files", ("valid.jpg", _image_bytes(), "image/jpeg")),
            ("files", ("fake.jpg", b"not an image", "image/jpeg")),
        ],
    )

    assert response.status_code == 422
    assert list(tmp_path.iterdir()) == []
    assert client.get(
        "/api/v1/photos/my-photos",
        headers={"X-Visitor-Access-Code": visitor["access_code"]},
    ).json() == []


def test_unsupported_image_format_is_rejected(
    client: TestClient, tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "storage_path", tmp_path)
    visitor = _register(client)
    response = _upload(
        client,
        visitor["access_code"],
        [("files", ("photo.tiff", _image_bytes("TIFF"), "image/tiff"))],
    )

    assert response.status_code == 415
    assert list(tmp_path.iterdir()) == []


def test_upload_size_limit_is_enforced(client: TestClient, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "storage_path", tmp_path)
    monkeypatch.setattr(settings, "max_image_size_mb", 1)
    visitor = _register(client)
    response = _upload(
        client,
        visitor["access_code"],
        [("files", ("large.jpg", b"x" * (1024 * 1024 + 1), "image/jpeg"))],
    )

    assert response.status_code == 413
    assert list(tmp_path.iterdir()) == []


def test_upload_count_limit_is_enforced(client: TestClient, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "storage_path", tmp_path)
    monkeypatch.setattr(settings, "max_photos_per_upload", 1)
    visitor = _register(client)
    response = _upload(
        client,
        visitor["access_code"],
        [
            ("files", ("first.jpg", _image_bytes(), "image/jpeg")),
            ("files", ("second.jpg", _image_bytes(), "image/jpeg")),
        ],
    )

    assert response.status_code == 413
    assert list(tmp_path.iterdir()) == []


def test_photo_metadata_is_private_to_its_visitor(
    client: TestClient, tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "storage_path", tmp_path)
    owner = _register(client, "Owner")
    other_visitor = _register(client, "Other visitor")
    upload_response = _upload(
        client,
        owner["access_code"],
        [("files", ("private.jpg", _image_bytes(), "image/jpeg"))],
    )
    photo_id = upload_response.json()[0]["id"]

    own_photo = client.get(
        f"/api/v1/photos/{photo_id}",
        headers={"X-Visitor-Access-Code": owner["access_code"]},
    )
    other_photo = client.get(
        f"/api/v1/photos/{photo_id}",
        headers={"X-Visitor-Access-Code": other_visitor["access_code"]},
    )
    other_list = client.get(
        "/api/v1/photos/my-photos",
        headers={"X-Visitor-Access-Code": other_visitor["access_code"]},
    )

    assert own_photo.status_code == 200
    assert other_photo.status_code == 404
    assert other_list.json() == []


def test_pending_photo_can_be_deleted_and_file_is_removed(
    client: TestClient, tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "storage_path", tmp_path)
    visitor = _register(client)
    upload_response = _upload(
        client,
        visitor["access_code"],
        [("files", ("remove.jpg", _image_bytes(), "image/jpeg"))],
    )
    photo = upload_response.json()[0]
    assert len(list(tmp_path.iterdir())) == 1

    response = client.delete(
        f"/api/v1/photos/{photo['id']}",
        headers={"X-Visitor-Access-Code": visitor["access_code"]},
    )

    assert response.status_code == 204
    assert list(tmp_path.iterdir()) == []
    assert client.get(
        f"/api/v1/photos/{photo['id']}",
        headers={"X-Visitor-Access-Code": visitor["access_code"]},
    ).status_code == 404


def test_approved_photo_cannot_be_deleted_by_visitor(
    client: TestClient, tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "storage_path", tmp_path)
    visitor = _register(client)
    upload_response = _upload(
        client,
        visitor["access_code"],
        [("files", ("approved.jpg", _image_bytes(), "image/jpeg"))],
    )
    photo_data = upload_response.json()[0]
    with client.app.state.test_session() as db:
        photo = db.get(Photo, uuid.UUID(photo_data["id"]))
        assert photo is not None
        photo.status = "approved"
        db.commit()

    response = client.delete(
        f"/api/v1/photos/{photo_data['id']}",
        headers={"X-Visitor-Access-Code": visitor["access_code"]},
    )

    assert response.status_code == 409
    assert len(list(tmp_path.iterdir())) == 1
    with client.app.state.test_session() as db:
        assert db.get(Photo, uuid.UUID(photo_data["id"])) is not None


def test_upload_requires_valid_visitor_access_code(client: TestClient):
    response = client.post(
        "/api/v1/photos/upload",
        headers={"X-Visitor-Access-Code": "ZZZZ-ZZZZ-ZZZZ-ZZZZ"},
        files=[("files", ("photo.jpg", _image_bytes(), "image/jpeg"))],
    )

    assert response.status_code == 401
