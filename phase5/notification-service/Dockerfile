# ===========================================================================
# Stage 1 - Builder: install dependencies with uv
# ===========================================================================
FROM python:3.13-slim AS builder

# Install uv (fast Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency manifest first for better layer caching
COPY pyproject.toml ./

# Install dependencies into a virtual environment
RUN uv venv /app/.venv && \
    uv pip install --python /app/.venv/bin/python -r pyproject.toml

# Copy application source
COPY src/ ./src/

# ===========================================================================
# Stage 2 - Production: slim runtime image
# ===========================================================================
FROM python:3.13-slim AS production

# Install curl for the HEALTHCHECK probe
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --system appuser && \
    useradd --system --gid appuser --create-home appuser

WORKDIR /app

# Copy virtual environment and source from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Ensure the venv python is on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER appuser

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
