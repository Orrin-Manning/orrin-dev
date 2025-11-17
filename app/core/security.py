from passlib.context import CryptContext

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _truncate_password(password: str) -> str:
    """
    Truncate password to 72 bytes for bcrypt compatibility.

    Bcrypt has a maximum password length of 72 bytes. This function ensures
    passwords are truncated to this limit before hashing/verification.
    """
    # Encode to bytes and truncate to 72 bytes, then decode back
    password_bytes = password.encode('utf-8')[:72]
    return password_bytes.decode('utf-8', errors='ignore')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    # Truncate to 72 bytes for bcrypt compatibility
    truncated_password = _truncate_password(plain_password)
    return pwd_context.verify(truncated_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt (auto-truncates to 72 bytes)."""
    # Truncate to 72 bytes for bcrypt compatibility
    truncated_password = _truncate_password(password)
    return pwd_context.hash(truncated_password)
