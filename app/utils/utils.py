import hashlib

from app.config import settings


def get_hash(text: str) -> str:
    text = text + settings.SECRET_HASH_KEY
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
