"""Tests for session fixation prevention."""

import re
import pytest


def extract_csrf_token(html: str) -> str | None:
    """Extract CSRF token from HTML form."""
    match = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
    return match.group(1) if match else None


def get_session_cookie(response) -> str | None:
    """Extract session cookie value from response."""
    for cookie in response.cookies.jar:
        if cookie.name == "session":
            return cookie.value
    return None


@pytest.mark.asyncio
async def test_login_regenerates_session(client):
    """Session ID should change after successful login."""
    # First, register a user
    get_response = await client.get("/register")
    csrf_token = extract_csrf_token(get_response.text)

    await client.post(
        "/register",
        data={
            "full_name": "Test User",
            "email": "session_test@example.com",
            "password": "password123",
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )

    # Logout to clear session
    await client.get("/logout")

    # Get session before login
    login_page = await client.get("/login")
    session_before = get_session_cookie(login_page)
    csrf_token = extract_csrf_token(login_page.text)

    # Login
    login_response = await client.post(
        "/login",
        data={
            "email": "session_test@example.com",
            "password": "password123",
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )

    session_after = get_session_cookie(login_response)

    # Session should have changed
    assert session_before != session_after, "Session ID should change after login"


@pytest.mark.asyncio
async def test_register_regenerates_session(client):
    """Session ID should change after successful registration."""
    # Get session before registration
    register_page = await client.get("/register")
    session_before = get_session_cookie(register_page)
    csrf_token = extract_csrf_token(register_page.text)

    # Register
    register_response = await client.post(
        "/register",
        data={
            "full_name": "New User",
            "email": "new_session_test@example.com",
            "password": "password123",
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )

    session_after = get_session_cookie(register_response)

    # Session should have changed
    assert session_before != session_after, "Session ID should change after registration"


@pytest.mark.asyncio
async def test_logout_clears_session(client):
    """Session should be cleared on logout."""
    # Register and login
    get_response = await client.get("/register")
    csrf_token = extract_csrf_token(get_response.text)

    await client.post(
        "/register",
        data={
            "full_name": "Logout Test",
            "email": "logout_test@example.com",
            "password": "password123",
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )

    # Get session while logged in
    home_response = await client.get("/")
    session_logged_in = get_session_cookie(home_response)

    # Logout
    logout_response = await client.get("/logout", follow_redirects=False)
    session_after_logout = get_session_cookie(logout_response)

    # Session should have changed (cleared)
    assert session_logged_in != session_after_logout, "Session should change after logout"
