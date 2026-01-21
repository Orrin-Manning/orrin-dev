"""Session management utilities."""

import secrets
from fastapi import Request


def regenerate_session(request: Request, preserve_keys: list[str] | None = None) -> None:
    """Regenerate the session to prevent session fixation attacks.

    Clears the current session and generates a new CSRF secret.
    Optionally preserves specified keys from the old session.

    Args:
        request: The FastAPI request object
        preserve_keys: List of session keys to preserve (e.g., ["user_id"])
    """
    # Save values we want to preserve
    preserved = {}
    if preserve_keys:
        for key in preserve_keys:
            if key in request.session:
                preserved[key] = request.session[key]

    # Clear the session (this invalidates the old session)
    request.session.clear()

    # Generate a new CSRF secret for the new session
    request.session["csrf_secret"] = secrets.token_hex(32)

    # Restore preserved values
    for key, value in preserved.items():
        request.session[key] = value
