from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from strawberry.fastapi import GraphQLRouter

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.graphql.schema import schema
from app.graphql.context import get_context
from app.web.routes import pages
from app.api.routes import health, item, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup: Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Shutdown: Dispose of the engine
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

# Add session middleware for authentication
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Static files
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

# GraphQL
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
)
app.include_router(graphql_app, prefix="/graphql")

# Web routes (HTML pages)
app.include_router(pages.router)

# API routes (JSON)
app.include_router(health.router)
app.include_router(item.router)
app.include_router(auth.router)
