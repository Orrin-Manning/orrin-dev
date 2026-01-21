"""Tests for CSRF protection on authentication forms."""

import re
import pytest


def extract_csrf_token(html: str) -> str | None:
    """Extract CSRF token from HTML form."""
    match = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
    return match.group(1) if match else None


@pytest.mark.asyncio
async def test_login_page_contains_csrf_token(client):
    """Login page should include a CSRF token in the form."""
    response = await client.get("/login")
    assert response.status_code == 200

    csrf_token = extract_csrf_token(response.text)
    assert csrf_token is not None, "CSRF token should be present in login form"
    assert len(csrf_token) > 20, "CSRF token should be a substantial string"


@pytest.mark.asyncio
async def test_register_page_contains_csrf_token(client):
    """Register page should include a CSRF token in the form."""
    response = await client.get("/register")
    assert response.status_code == 200

    csrf_token = extract_csrf_token(response.text)
    assert csrf_token is not None, "CSRF token should be present in register form"
    assert len(csrf_token) > 20, "CSRF token should be a substantial string"


@pytest.mark.asyncio
async def test_login_rejects_missing_csrf_token(client):
    """Login POST without CSRF token should be rejected with 403."""
    response = await client.post(
        "/login",
        data={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 403
    assert "Invalid form submission" in response.text


@pytest.mark.asyncio
async def test_register_rejects_missing_csrf_token(client):
    """Register POST without CSRF token should be rejected with 403."""
    response = await client.post(
        "/register",
        data={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 403
    assert "Invalid form submission" in response.text


@pytest.mark.asyncio
async def test_login_rejects_invalid_csrf_token(client):
    """Login POST with invalid CSRF token should be rejected with 403."""
    # First get the page to establish a session
    await client.get("/login")

    # Submit with a fake token
    response = await client.post(
        "/login",
        data={
            "email": "test@example.com",
            "password": "password123",
            "csrf_token": "invalid-fake-token",
        },
    )
    assert response.status_code == 403
    assert "Invalid form submission" in response.text


@pytest.mark.asyncio
async def test_register_rejects_invalid_csrf_token(client):
    """Register POST with invalid CSRF token should be rejected with 403."""
    # First get the page to establish a session
    await client.get("/register")

    # Submit with a fake token
    response = await client.post(
        "/register",
        data={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "password123",
            "csrf_token": "invalid-fake-token",
        },
    )
    assert response.status_code == 403
    assert "Invalid form submission" in response.text


@pytest.mark.asyncio
async def test_login_accepts_valid_csrf_token(client):
    """Login POST with valid CSRF token should be processed."""
    # Get the login page to get the CSRF token
    get_response = await client.get("/login")
    csrf_token = extract_csrf_token(get_response.text)
    assert csrf_token is not None

    # Submit with valid token (login will fail due to wrong credentials, but not 403)
    response = await client.post(
        "/login",
        data={
            "email": "test@example.com",
            "password": "password123",
            "csrf_token": csrf_token,
        },
    )
    # Should get 200 with error message, not 403 CSRF rejection
    assert response.status_code == 200
    assert "Incorrect email or password" in response.text
    assert "Invalid form submission" not in response.text


@pytest.mark.asyncio
async def test_register_accepts_valid_csrf_token(client):
    """Register POST with valid CSRF token should be processed."""
    # Get the register page to get the CSRF token
    get_response = await client.get("/register")
    csrf_token = extract_csrf_token(get_response.text)
    assert csrf_token is not None

    # Submit with valid token
    response = await client.post(
        "/register",
        data={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "password123",
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )
    # Should succeed with redirect (303), not 403 CSRF rejection
    assert response.status_code == 303
    assert response.headers.get("location") == "/"


@pytest.mark.asyncio
async def test_csrf_token_reuse_across_same_session(client):
    """CSRF token should be valid for multiple submissions in same session."""
    # Get token from login page
    get_response = await client.get("/login")
    csrf_token = extract_csrf_token(get_response.text)

    # First submission (fails auth but passes CSRF)
    response1 = await client.post(
        "/login",
        data={
            "email": "test@example.com",
            "password": "wrong",
            "csrf_token": csrf_token,
        },
    )
    assert response1.status_code == 200
    assert "Invalid form submission" not in response1.text

    # Second submission with same token should also work
    response2 = await client.post(
        "/login",
        data={
            "email": "test@example.com",
            "password": "wrong",
            "csrf_token": csrf_token,
        },
    )
    assert response2.status_code == 200
    assert "Invalid form submission" not in response2.text


@pytest.mark.asyncio
async def test_csrf_token_rejected_without_session(client):
    """CSRF token from one session should not work in another."""
    # Get token from first session
    response1 = await client.get("/login")
    csrf_token = extract_csrf_token(response1.text)

    # Create a new client (new session) and try to use the old token
    from httpx import ASGITransport, AsyncClient
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as new_client:
        # Submit with token from different session
        response = await new_client.post(
            "/login",
            data={
                "email": "test@example.com",
                "password": "password123",
                "csrf_token": csrf_token,
            },
        )
        # Should be rejected
        assert response.status_code == 403
        assert "Invalid form submission" in response.text
