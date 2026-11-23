# Multi-Stage Hardened Production Dockerfile for ProdForge
# Enterprise Container Standards: Non-Root Execution, Minimal Attack Surface, Reproducible Wheel Build

# ─── Stage 1: Build Wheels ──────────────────────────────────────────────────
FROM python:3.12-slim-bookworm AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir --upgrade pip build wheel setuptools && \
    python -m build --wheel

# ─── Stage 2: Hardened Runtime Container ────────────────────────────────────
FROM python:3.12-slim-bookworm AS runner

# Security: Create non-root system user and group (UID/GID 10001)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /sbin/nologin -m -d /home/appuser appuser

WORKDIR /workspace

# Install built package wheel from builder stage
COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && \
    rm -rf /tmp/*.whl

# Setup workspace permissions
RUN chown -R appuser:appgroup /workspace /home/appuser

# Switch to unprivileged user
USER appuser:appgroup

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/appuser/.local/bin:${PATH}"

EXPOSE 8000

# Default entrypoint is the ProdForge CLI
ENTRYPOINT ["prodforge"]
CMD ["studio", "--host", "0.0.0.0", "--port", "8000"]
