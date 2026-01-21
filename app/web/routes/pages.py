from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from app.db.session import get_db
from app.db.crud.user import create_user, authenticate_user, get_user_by_email, get_user_by_id
from app.schemas.user import UserCreate
from app.core.csrf import generate_csrf_token, validate_csrf_token
from app.core.session import regenerate_session

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="app/web/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    user = None
    user_id = request.session.get("user_id")
    if user_id:
        user = await get_user_by_id(db, user_id)
    return templates.TemplateResponse(
        request=request, name="home.html", context={"user": user}
    )


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Show registration form."""
    csrf_token = generate_csrf_token(request)
    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context={"csrf_token": csrf_token},
    )


@router.post("/register")
async def register_submit(
    request: Request,
    full_name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    csrf_token: Annotated[str | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
):
    """Handle registration form submission."""
    # Validate CSRF token
    if not validate_csrf_token(request, csrf_token):
        new_csrf_token = generate_csrf_token(request)
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={"error": "Invalid form submission. Please try again.", "csrf_token": new_csrf_token},
            status_code=403,
        )

    # Check if user already exists
    existing_user = await get_user_by_email(db, email)
    if existing_user:
        new_csrf_token = generate_csrf_token(request)
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={"error": "Email already registered", "csrf_token": new_csrf_token},
        )

    # Validate password length
    if len(password) < 8:
        new_csrf_token = generate_csrf_token(request)
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={"error": "Password must be at least 8 characters", "csrf_token": new_csrf_token},
        )

    # Create user
    try:
        user_create = UserCreate(email=email, password=password, full_name=full_name)
        user = await create_user(db, user_create)

        # Regenerate session to prevent session fixation, then log in
        regenerate_session(request)
        request.session["user_id"] = user.id

        # Redirect to home page
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        new_csrf_token = generate_csrf_token(request)
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={"error": f"Registration failed: {str(e)}", "csrf_token": new_csrf_token},
        )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Show login form."""
    csrf_token = generate_csrf_token(request)
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={"csrf_token": csrf_token},
    )


@router.post("/login")
async def login_submit(
    request: Request,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    csrf_token: Annotated[str | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
):
    """Handle login form submission."""
    # Validate CSRF token
    if not validate_csrf_token(request, csrf_token):
        new_csrf_token = generate_csrf_token(request)
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={"error": "Invalid form submission. Please try again.", "csrf_token": new_csrf_token},
            status_code=403,
        )

    user = await authenticate_user(db, email, password)

    if not user:
        new_csrf_token = generate_csrf_token(request)
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={"error": "Incorrect email or password", "csrf_token": new_csrf_token},
        )

    # Regenerate session to prevent session fixation, then log in
    regenerate_session(request)
    request.session["user_id"] = user.id

    # Redirect to home page
    return RedirectResponse(url="/", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    """Log out the current user."""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
