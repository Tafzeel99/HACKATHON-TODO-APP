# Stage 1: Build dependencies
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml .
RUN uv venv .venv && uv pip install --python .venv/bin/python -r pyproject.toml

COPY src/ src/

# Stage 2: Production
FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /app

COPY --from=builder /app/.venv .venv
COPY --from=builder /app/src src/

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8003

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

USER appuser

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8003"]
