FROM python:3.14-slim
WORKDIR /code

# TODO: Remove gcc once asyncpg has Python 3.14 wheels (check https://pypi.org/project/asyncpg/#files for cp314)
# Install build dependencies for packages that need compilation (asyncpg, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies
COPY pyproject.toml uv.lock /code/
RUN uv sync --frozen

# Copy application
COPY ./app /code/app

CMD ["uv", "run", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
