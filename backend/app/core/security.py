import base64
import binascii
import hashlib
import hmac
import json
import secrets
import time


ACCESS_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
ACCESS_CODE_LENGTH = 16
ADMIN_PASSWORD_HASH_ITERATIONS = 600_000


def generate_access_code() -> str:
    characters = "".join(
        secrets.choice(ACCESS_CODE_ALPHABET) for _ in range(ACCESS_CODE_LENGTH)
    )
    return "-".join(characters[index : index + 4] for index in range(0, 16, 4))


def normalize_access_code(access_code: str) -> str:
    return access_code.replace("-", "").replace(" ", "").upper()


def hash_access_code(access_code: str) -> str:
    normalized_code = normalize_access_code(access_code)
    return hashlib.sha256(normalized_code.encode("ascii")).hexdigest()


def hash_admin_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, ADMIN_PASSWORD_HASH_ITERATIONS
    )
    return "$".join(
        (
            "pbkdf2_sha256",
            str(ADMIN_PASSWORD_HASH_ITERATIONS),
            base64.urlsafe_b64encode(salt).decode("ascii"),
            base64.urlsafe_b64encode(password_hash).decode("ascii"),
        )
    )


def verify_admin_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iteration_text, salt_text, expected_hash_text = stored_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iteration_text)
        if iterations < ADMIN_PASSWORD_HASH_ITERATIONS:
            return False
        salt = base64.urlsafe_b64decode(salt_text)
        expected_hash = base64.urlsafe_b64decode(expected_hash_text)
    except (ValueError, binascii.Error):
        return False

    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations
    )
    return hmac.compare_digest(password_hash, expected_hash)


def create_admin_access_token(
    username: str, secret: str, expires_minutes: int
) -> str:
    if len(secret) < 32:
        raise ValueError("ADMIN_TOKEN_SECRET must contain at least 32 characters")
    payload = {
        "sub": username,
        "exp": int(time.time()) + expires_minutes * 60,
    }
    encoded_payload = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    ).rstrip(b"=").decode("ascii")
    signature = hmac.new(
        secret.encode("utf-8"), encoded_payload.encode("ascii"), hashlib.sha256
    ).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
    return f"{encoded_payload}.{encoded_signature}"


def get_admin_token_username(token: str, secret: str) -> str | None:
    if len(secret) < 32:
        raise ValueError("ADMIN_TOKEN_SECRET must contain at least 32 characters")
    try:
        encoded_payload, encoded_signature = token.split(".", maxsplit=1)
        signature = base64.urlsafe_b64decode(
            encoded_signature + "=" * (-len(encoded_signature) % 4)
        )
        expected_signature = hmac.new(
            secret.encode("utf-8"),
            encoded_payload.encode("ascii"),
            hashlib.sha256,
        ).digest()
        if not hmac.compare_digest(signature, expected_signature):
            return None

        payload_bytes = base64.urlsafe_b64decode(
            encoded_payload + "=" * (-len(encoded_payload) % 4)
        )
        payload = json.loads(payload_bytes)
        if not isinstance(payload, dict):
            return None
        username = payload.get("sub")
        expires_at = payload.get("exp")
        if (
            not isinstance(username, str)
            or not isinstance(expires_at, int)
            or expires_at <= int(time.time())
        ):
            return None
        return username
    except (ValueError, TypeError, binascii.Error, json.JSONDecodeError):
        return None
