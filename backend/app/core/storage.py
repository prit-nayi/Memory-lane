import logging
import os
import re
import tempfile
import uuid
import warnings
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from starlette.datastructures import UploadFile

from app.core.config import PROJECT_ROOT, settings


logger = logging.getLogger(__name__)
SUPPORTED_FORMATS = {
    "JPEG": ("image/jpeg", ".jpg"),
    "PNG": ("image/png", ".png"),
    "WEBP": ("image/webp", ".webp"),
}
STORAGE_KEY_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.(jpg|png|webp)"
)
CHUNK_SIZE = 64 * 1024


class InvalidImageError(ValueError):
    pass


class UnsupportedImageError(ValueError):
    pass


class ImageTooLargeError(ValueError):
    pass


class PhotoStorageError(RuntimeError):
    pass


@dataclass(frozen=True)
class StagedPhoto:
    temporary_path: Path
    storage_key: str
    original_filename: str
    content_type: str
    file_size: int


def get_storage_root() -> Path:
    path = settings.storage_path
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def stage_upload(upload: UploadFile) -> StagedPhoto:
    temporary_path: Path | None = None
    try:
        root = get_storage_root()
        root.mkdir(parents=True, exist_ok=True)
        size = 0
        max_size = settings.max_image_size_mb * 1024 * 1024
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=".upload-", suffix=".tmp", dir=root, delete=False
        ) as staged_file:
            temporary_path = Path(staged_file.name)
            while chunk := upload.file.read(CHUNK_SIZE):
                size += len(chunk)
                if size > max_size:
                    raise ImageTooLargeError(
                        f"Each image must be no larger than "
                        f"{settings.max_image_size_mb} MB"
                    )
                staged_file.write(chunk)
    except ImageTooLargeError:
        _remove_temporary_file(temporary_path)
        raise
    except OSError as exc:
        _remove_temporary_file(temporary_path)
        raise PhotoStorageError("Could not write the uploaded image") from exc

    if temporary_path is None:
        raise PhotoStorageError("Could not create a staged image file")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(temporary_path) as image:
                image_format = image.format
                if image_format not in SUPPORTED_FORMATS:
                    raise UnsupportedImageError(
                        "Only JPEG, PNG, and WebP images are supported"
                    )
                image.verify()
            with Image.open(temporary_path) as image:
                image.load()
    except (InvalidImageError, UnsupportedImageError, ImageTooLargeError):
        _remove_temporary_file(temporary_path)
        raise
    except (
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        UnidentifiedImageError,
        OSError,
        SyntaxError,
    ) as exc:
        _remove_temporary_file(temporary_path)
        raise InvalidImageError("The uploaded file is not a valid image") from exc

    content_type, extension = SUPPORTED_FORMATS[image_format]
    original_filename = (upload.filename or "upload").replace("\\", "/").rsplit(
        "/", 1
    )[-1]
    original_filename = original_filename[:255] or "upload"
    return StagedPhoto(
        temporary_path=temporary_path,
        storage_key=f"{uuid.uuid4()}{extension}",
        original_filename=original_filename,
        content_type=content_type,
        file_size=size,
    )


def finalize_upload(photo: StagedPhoto) -> None:
    destination = get_storage_root() / photo.storage_key
    try:
        os.replace(photo.temporary_path, destination)
    except OSError as exc:
        raise PhotoStorageError("Could not store the uploaded image") from exc


def remove_upload(storage_key: str) -> None:
    if not STORAGE_KEY_PATTERN.fullmatch(storage_key):
        raise PhotoStorageError("Stored image key is invalid")
    path = get_storage_root() / storage_key
    try:
        path.unlink(missing_ok=True)
    except OSError as exc:
        raise PhotoStorageError("Could not remove the stored image") from exc


def _remove_temporary_file(path: Path | None) -> None:
    if path is None:
        return
    try:
        path.unlink(missing_ok=True)
    except OSError as exc:
        logger.exception("Could not remove staged upload file %s", path)
        raise PhotoStorageError("Could not clean up the staged image") from exc


def discard_staged_upload(photo: StagedPhoto) -> None:
    _remove_temporary_file(photo.temporary_path)
