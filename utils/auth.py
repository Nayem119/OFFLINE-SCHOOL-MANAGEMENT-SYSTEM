import hashlib
import hmac
import secrets

_PREFIX = "pbkdf2_sha256$"
_ITERATIONS = 240000


def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return f"{_PREFIX}{_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password, stored):
    if not stored:
        return False
    if not stored.startswith(_PREFIX):
        return hmac.compare_digest(password, stored)
    try:
        algorithm, iterations, salt_hex, digest_hex = stored.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False
