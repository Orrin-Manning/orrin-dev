"""CSRF protection utilities using itsdangerous for token generation and validation."""

import secrets
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Request, HTTPException

from app.core.config import settings

# Token expiration time in seconds (1 hour)
CSRF_TOKEN_EXPIRY = 3600

# Create serializer with SECRET_KEY
_serializer = URLSafeTimedSerializer(settings.SECRET_KEY, salt="csrf-token")


def generate_csrf_token(request: Request) -> str:
    """Generate a CSRF token and store the secret in the session.

    The token is a signed value containing a random secret that is also
    stored in the session. On validation, we verify both the signature
    and that the secret matches the session.
    """
    # Generate a random secret for this session if not present
    if "csrf_secret" not in request.session:
        request.session["csrf_secret"] = secrets.token_hex(32)

    csrf_secret = request.session["csrf_secret"]

    # Create a signed token containing the secret
    token = _serializer.dumps(csrf_secret)
    return token


def validate_csrf_token(request: Request, token: str | None) -> bool:
    """Validate a CSRF token against the session secret.

    Args:
        request: The FastAPI request object
        token: The CSRF token from the form submission

    Returns:
        True if valid, False otherwise
    """
    if not token:
        return False

    session_secret = request.session.get("csrf_secret")
    if not session_secret:
        return False

    try:
        # Unsign the token and verify it matches the session secret
        token_secret = _serializer.loads(token, max_age=CSRF_TOKEN_EXPIRY)
        return secrets.compare_digest(token_secret, session_secret)
    except (BadSignature, SignatureExpired):
        return False


async def require_csrf_token(request: Request, csrf_token: str | None) -> None:
    """Dependency to require and validate CSRF token.

    Raises HTTPException with 403 status if token is invalid.
    """
    if not validate_csrf_token(request, csrf_token):
        raise HTTPException(
            status_code=403,
            detail="CSRF token missing or invalid"
        )
