from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter

from app.graphql.schema import schema
from app.graphql.context import get_context
from app.web.routes import pages
from app.api.routes import health, item

app = FastAPI()

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
