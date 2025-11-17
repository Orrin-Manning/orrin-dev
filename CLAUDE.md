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
# First time: Create .env file with production credentials
cp .env.example .env
# Edit .env with secure credentials for PROD_POSTGRES_USER and PROD_POSTGRES_PASSWORD

docker compose --profile prod up --build
```

**Connecting to PostgreSQL:**

Development (local):
```bash
# If psql installed locally
psql postgresql://devuser:devpass@localhost:5432/orrin_dev

# Or via Docker
docker compose exec postgres-dev psql -U devuser -d orrin_dev
```

Production (on Pi via SSH tunnel):
```bash
# Terminal 1: Create SSH tunnel
ssh -L 5433:localhost:5432 pi@your-pi-ip

# Terminal 2: Connect via tunnel
psql postgresql://[username]:[password]@localhost:5433/orrin_prod
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

### Issue Tracking with GitLab

This project uses GitLab for issue tracking. The `glab` CLI tool is installed and configured.

**Viewing issues:**
```bash
# List all open issues
glab issue list

# List security issues by priority
glab issue list --label security
glab issue list --label critical
glab issue list --label high
glab issue list --label medium

# View specific issue details
glab issue view <issue-number>

# View issue in browser
glab issue view <issue-number> --web
```

**Working on issues:**
```bash
# Create a branch for an issue
glab issue view <issue-number>
# Then create branch: git checkout -b issue-<number>-description

# Close an issue after fix
glab issue close <issue-number> --comment "Fixed by implementing..."
```

**Security Issues:**
Issues #1-13 track security vulnerabilities and bugs identified in the authentication system:
- **Critical (3 issues)**: #1 (CSRF), #2 (SECRET_KEY), #3 (Session Fixation)
- **High (2 issues)**: #4 (Error Messages), #5 (Timing Attack)
- **Medium (4 issues)**: #6-9 (User Enumeration, Rate Limiting, Security Headers, Session Config)
- **Low (2 issues)**: #10-11 (Password Requirements, Account Lockout)
- **Bugs (2 issues)**: #12-13 (Password Truncation, Exception Handling)

**IMPORTANT**: When starting a new Claude Code session to work on these issues, use explicit prompts like:
- "Use glab to list all security issues"
- "Fetch GitLab issue #1 with glab and let's implement the fix"
- "Run 'glab issue list --label critical' and show the results"

Simply saying "list security issues" will trigger a fresh security audit instead of fetching existing GitLab issues.

## Architecture

### Application Structure

The FastAPI application is initialized in `app/main.py` and integrates three routing systems:

1. **Web Routes** (`app/web/routes/`): HTML pages served via Jinja2 templates
   - Templates directory: `app/web/templates/`
   - Static files: `app/web/static/`
   - Routes are excluded from OpenAPI schema (`include_in_schema=False`)

2. **REST API Routes** (`app/api/routes/`): JSON endpoints with OpenAPI documentation
   - `health.py`: Health check endpoint
   - `item.py`: Item management (uses legacy token auth via `get_token_header`)
   - `auth.py`: Authentication endpoints (register, login, logout, me)
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
- **postgres-dev**: PostgreSQL 18 database
  - Exposed on port 5432 for local access
  - Credentials: `devuser:devpass` (can be overridden via `.env`)
  - Database: `orrin_dev`
  - Persistent data via Docker volume `postgres-dev-data`
- **app-dev**: FastAPI application with hot reload
  - Source code mounted as volume for live updates
  - Direct access on port 8000
  - Runs `fastapi dev` command
  - `DATABASE_URL` environment variable provided

**Production Profile (`prod`):**
- **postgres-prod**: PostgreSQL 18 database
  - Internal only (not exposed outside Docker network)
  - Credentials: **Must be set via `.env` file** (no defaults)
  - Database: `orrin_prod`
  - Persistent data via Docker volume `postgres-prod-data`
- **app-prod**: FastAPI application in production mode
  - `DATABASE_URL` environment variable provided
- **nginx**: Reverse proxy routing traffic to the app
  - Configuration: `nginx.conf` proxies requests to `app-prod:8000`
  - Domain: Configured for `orrin.dev` and `www.orrin.dev`
  - Accessible on port 80 through nginx

**Environment Variables:**

See `.env.example` for required variables.

Application settings:
- `SECRET_KEY` - Secret key for session signing (change in production!)
- `DATABASE_URL` - PostgreSQL async connection string

Production requires a `.env` file with secure credentials:
- `PROD_POSTGRES_USER` (required, no default)
- `PROD_POSTGRES_PASSWORD` (required, no default)
- `PROD_POSTGRES_DB` (default: `orrin_prod`)

Development has sensible defaults but can be customized:
- `DEV_POSTGRES_USER` (default: `devuser`)
- `DEV_POSTGRES_PASSWORD` (default: `devpass`)
- `DEV_POSTGRES_DB` (default: `orrin_dev`)
- `DEV_POSTGRES_PORT` (default: `5432`)

### Authentication

The application uses **session-based authentication** with the following components:

**Database Layer:**
- User model: `app/db/models/user.py` (email, hashed_password, full_name, timestamps)
- CRUD operations: `app/db/crud/user.py` (create_user, authenticate_user, get_user_by_email, get_user_by_id)
- Password hashing: `app/core/security.py` using bcrypt via passlib

**Authentication Endpoints (REST API):**
- `POST /api/auth/register` - Register new user (auto-login)
- `POST /api/auth/login` - Authenticate and create session
- `POST /api/auth/logout` - Clear session
- `GET /api/auth/me` - Get current user info

**Web Routes (HTML):**
- `GET/POST /register` - Registration page and form submission
- `GET/POST /login` - Login page and form submission
- `GET /logout` - Logout and redirect

**Session Management:**
- Uses Starlette's `SessionMiddleware` with SECRET_KEY from settings
- User ID stored in session: `request.session["user_id"]`
- Dependencies in `app/api/dependencies.py`:
  - `get_current_user()` - Returns User or raises 401
  - `get_current_user_optional()` - Returns User or None
  - `get_token_header()` - Legacy token auth (kept for backwards compatibility with item routes)

**Database Migrations:**
- Alembic configured for async SQLAlchemy
- Run migrations: `uv run alembic upgrade head`
- Create new migration: `uv run alembic revision --autogenerate -m "description"`

**Configuration:**
- `SECRET_KEY` - Required for session security (set in .env)
- `DATABASE_URL` - PostgreSQL connection string (default: dev database)

## Technology Stack

- **Python**: 3.13+
- **Web Framework**: FastAPI with standard extras
- **GraphQL**: Strawberry GraphQL
- **Templates**: Jinja2
- **Database**: PostgreSQL 18 (via Docker), SQLAlchemy (async), Alembic (migrations)
- **Authentication**: Session-based auth, Passlib (bcrypt password hashing)
- **ML Libraries**: NumPy, Pandas, Scikit-learn, PyTorch (torchvision), Matplotlib
- **Development**: Jupyter, Ruff
- **Deployment**: Docker, nginx, uv package manager
