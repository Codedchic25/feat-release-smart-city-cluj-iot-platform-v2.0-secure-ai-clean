# ============================================================================
# STAGE 1 — Builder (Fast Python Dependency Installation Layer)
# ============================================================================
FROM python:3.12-slim-bookworm AS builder

# Prevent Python from writing pyc files and enable immediate stdout/stderr flushing
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /workspace

# Install the modern dependency manager 'uv' seamlessly
RUN pip install --no-cache-dir uv==0.5.11

# Copy only the dependency definition ledgers to maximize Docker caching efficiency
COPY pyproject.toml uv.lock ./

# Install project production dependencies using uv native system sync capabilities.
# Excludes development groups (--no-dev) to minimize the final production footprint.
RUN uv pip install --system --no-cache --no-dev .

# ============================================================================
# STAGE 2 — Production Layer (Stable, Light, and Secure Runtime Environment)
# ============================================================================
FROM python:3.12-slim-bookworm

WORKDIR /workspace

# Install minimal system utilities required for health monitoring, then purge apt caches
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Establish strict production environment variables for Streamlit and Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Copy the pre-compiled packages and executable binaries from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the complete application codebase into the active execution workspace
COPY . /workspace/

# Expose the standard Streamlit communication port
EXPOSE 8501

# Validate production container operational readiness through structural health checks
HEALTHCHECK --interval=30s \
    --timeout=10s \
    --start-period=30s \
    --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Execute database seeding protocol before launching the Streamlit interface engine
CMD ["sh", "-c", "python seed_db.py && streamlit run main.py"]
