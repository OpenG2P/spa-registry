import base64
import hashlib
import hmac

from cryptography.fernet import Fernet

ENC_PREFIX = "enc:v1:"


def identifier_hash(normalized: str, key: str) -> str:
    return hmac.new(key.encode(), normalized.encode(), hashlib.sha256).hexdigest()


def _fernet(key: str) -> Fernet:
    digest = hashlib.sha256(key.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_identifier(normalized: str, key: str) -> str:
    if not key:
        raise ValueError("financial_address_encryption_key is not set")
    token = _fernet(key).encrypt(normalized.encode()).decode()
    return ENC_PREFIX + token


def decrypt_identifier(stored: str, key: str) -> str:
    if not stored or not stored.startswith(ENC_PREFIX):
        return stored
    if not key:
        raise ValueError("financial_address_encryption_key is not set")
    token = stored[len(ENC_PREFIX) :]
    return _fernet(key).decrypt(token.encode()).decode()
