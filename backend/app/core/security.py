import hashlib
import secrets


ACCESS_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
ACCESS_CODE_LENGTH = 16


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
