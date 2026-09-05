"""
Hashing and checksum utilities.
"""
import hashlib
from pathlib import Path


def hash_content(content: str | bytes) -> str:
    """Return SHA-256 hash of text or bytes content."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def hash_file(file_path: Path) -> str:
    """Return SHA-256 hash of a file on disk."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()
