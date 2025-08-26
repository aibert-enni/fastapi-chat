import hashlib
import secrets
from typing import Tuple


def generate_verification_token() -> Tuple[str, str]:
    raw = secrets.token_urlsafe(32)
    hashed = hash_token(raw)
    return raw, hashed


def hash_token(raw_token: str):
    return hashlib.sha256(raw_token.encode()).hexdigest()
