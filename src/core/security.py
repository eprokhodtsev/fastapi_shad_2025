import hashlib


def get_password_hash(password: str) -> str:
    """Generate a simple hash for the password."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify the password against the hash."""
    return get_password_hash(plain_password) == hashed_password 