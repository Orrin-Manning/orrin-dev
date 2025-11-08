FROM python:3.14-slim
WORKDIR /code

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies
COPY pyproject.toml uv.lock /code/
RUN uv sync --frozen --no-install-project

# Copy application
COPY ./app /code/app

CMD ["uv", "run", "fastapi", "run", "app/main.py", "--port", "80"]
