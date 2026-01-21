from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from app.db.session import get_db
from app.db.crud.user import create_user, authenticate_user, get_user_by_email
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.api.dependencies import get_current_user
from app.db.models.user import User
from app.core.session import regenerate_session

router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"],
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Register a new user and automatically log them in."""
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create the user
    user = await create_user(db, user_create)

    # Regenerate session to prevent session fixation, then log in
    regenerate_session(request)
    request.session["user_id"] = user.id

    return user


@router.post("/login", response_model=UserResponse)
async def login(
    user_login: UserLogin,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Authenticate a user and create a session."""
    user = await authenticate_user(db, user_login.email, user_login.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Regenerate session to prevent session fixation, then log in
    regenerate_session(request)
    request.session["user_id"] = user.id

    return user


@router.post("/logout")
async def logout(request: Request):
    """Log out the current user by clearing their session."""
    request.session.clear()
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get the current authenticated user's information."""
    return current_user
