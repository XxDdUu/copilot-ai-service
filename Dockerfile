FROM python:3.13-slim

WORKDIR /app

# Cài uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency trước để tận dụng cache
COPY pyproject.toml uv.lock ./

ENV UV_INDEX=https://download.pytorch.org/whl/cpu

RUN uv sync --frozen

# Copy source code
COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]