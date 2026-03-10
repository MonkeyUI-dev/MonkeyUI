"""
Encryption utilities for sensitive data storage.

Uses Fernet symmetric encryption with a key derived from Django's SECRET_KEY.
This ensures that encrypted data in the database cannot be read without
the application's secret key.
"""
import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def _get_fernet_key() -> bytes:
    """
    Derive a Fernet-compatible key from Django's SECRET_KEY.

    Uses SHA-256 to produce a 32-byte digest, then base64url-encodes it
    to create a valid Fernet key (44 URL-safe base64-encoded bytes).
    """
    secret = settings.SECRET_KEY.encode()
    digest = hashlib.sha256(secret).digest()
    return base64.urlsafe_b64encode(digest)


def _get_fernet() -> Fernet:
    """Return a Fernet instance using the derived key."""
    return Fernet(_get_fernet_key())


def encrypt_value(plaintext: str) -> str:
    """
    Encrypt a plaintext string and return a URL-safe base64-encoded token.

    Args:
        plaintext: The string to encrypt.

    Returns:
        The encrypted value as a URL-safe base64 string.
    """
    if not plaintext:
        return ""
    f = _get_fernet()
    return f.encrypt(plaintext.encode()).decode()


def decrypt_value(token: str) -> str:
    """
    Decrypt a Fernet token back to the original plaintext string.

    Args:
        token: The encrypted value (URL-safe base64 string).

    Returns:
        The decrypted plaintext string.

    Raises:
        InvalidToken: If the token is invalid or was encrypted with
                      a different key.
    """
    if not token:
        return ""
    f = _get_fernet()
    return f.decrypt(token.encode()).decode()
