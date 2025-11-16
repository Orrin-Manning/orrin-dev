# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI application that serves multiple interfaces:
- **REST API** endpoints (JSON responses)
- **GraphQL API** using Strawberry GraphQL
- **Web routes** serving HTML pages with Jinja2 templates
- **Static files** served from `app/web/static`

The project also serves as a machine learning learning environment, with goals to understand fundamental ML concepts and practice with real datasets.

## Development Commands

### Running the Application

**Local development:**
```bash
uv run fastapi dev app/main.py
```

**Production mode:**
```bash
uv run fastapi run app/main.py --port 8000
```

**Docker Compose:**

Development mode (hot reload, direct access on port 8000):
```bash
docker compose --profile dev up
```

Production mode (with nginx reverse proxy on port 80):
```bash
docker compose --profile prod up --build
```

### Dependency Management

This project uses `uv` for dependency management:

```bash
# Sync dependencies from uv.lock
uv sync

# Add a new dependency
uv add <package-name>

# Update dependencies
uv lock --upgrade
```

### Code Quality

**Linting and formatting:**
```bash
uv run ruff check .
uv run ruff format .
```

## Architecture

### Application Structure

The FastAPI application is initialized in `app/main.py` and integrates three routing systems:

1. **Web Routes** (`app/web/routes/`): HTML pages served via Jinja2 templates
   - Templates directory: `app/web/templates/`
   - Static files: `app/web/static/`
   - Routes are excluded from OpenAPI schema (`include_in_schema=False`)

2. **REST API Routes** (`app/api/routes/`): JSON endpoints with OpenAPI documentation
   - `health.py`: Health check endpoint
   - `item.py`: Item management (uses dependency injection for auth via `get_token_header`)
   - Dependencies defined in `app/api/dependencies.py`

3. **GraphQL** (`app/graphql/`): Strawberry GraphQL mounted at `/graphql`
   - Schema: `app/graphql/schema.py` defines Query and Mutation types
   - Context: `app/graphql/context.py` provides request context to resolvers
   - Queries: `app/graphql/queries/`
   - Mutations: `app/graphql/mutations/`
   - Types: `app/graphql/types/`

### Key Integration Points

- **Main Application** (`app/main.py`): All routers are included here
- **GraphQL Context**: Custom context is provided via `get_context` function
- **Static Files**: Mounted at `/static` path using FastAPI's `StaticFiles`
- **Dependencies**: API routes use FastAPI's dependency injection system (see `app/api/dependencies.py`)

### Docker Setup

The application uses Docker Compose with two profiles:

**Development Profile (`dev`):**
- **app-dev**: FastAPI application with hot reload
- Source code mounted as volume for live updates
- Direct access on port 8000
- Runs `fastapi dev` command

**Production Profile (`prod`):**
- **app-prod**: FastAPI application in production mode
- **nginx**: Reverse proxy routing traffic to the app
- Configuration: `nginx.conf` proxies requests to `app-prod:8000`
- Domain: Configured for `orrin.dev` and `www.orrin.dev`
- Accessible on port 80 through nginx

### Authentication

Currently uses a simple token-based auth via the `get_token_header` dependency:
- Protected routes require `X-Token` header
- Token value: `"fake-super-secret-token"` (hardcoded, development only)

## Technology Stack

- **Python**: 3.14+
- **Web Framework**: FastAPI with standard extras
- **GraphQL**: Strawberry GraphQL
- **Templates**: Jinja2
- **ML Libraries**: NumPy, Pandas, Scikit-learn, PyTorch (torchvision), Matplotlib
- **Development**: Jupyter, Ruff
- **Deployment**: Docker, nginx, uv package manager
