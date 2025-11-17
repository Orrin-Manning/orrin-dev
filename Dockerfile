FROM python:3.13-slim
WORKDIR /code

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies
COPY pyproject.toml uv.lock /code/
RUN uv sync --frozen

# Copy application
COPY ./app /code/app

CMD ["uv", "run", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
