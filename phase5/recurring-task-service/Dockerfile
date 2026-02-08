# =============================================================================
# Recurring Task Service - Multi-stage Docker Build
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Builder - install dependencies
# ---------------------------------------------------------------------------
FROM python:3.13-slim AS builder

WORKDIR /app

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv

# Copy dependency manifests
COPY pyproject.toml ./

# Install dependencies into a virtual environment
RUN uv venv /app/.venv && \
    . /app/.venv/bin/activate && \
    uv pip install --no-cache .

# Copy application source
COPY src/ ./src/

# ---------------------------------------------------------------------------
# Stage 2: Production - minimal runtime image
# ---------------------------------------------------------------------------
FROM python:3.13-slim AS production

WORKDIR /app

# Create a non-root user for security
RUN groupadd --system appuser && \
    useradd --system --gid appuser --no-create-home appuser

# Install curl for healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy virtual environment and source from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

# Ensure the venv is on the PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002"]