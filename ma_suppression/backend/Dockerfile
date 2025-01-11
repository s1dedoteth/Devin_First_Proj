FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir wheel && \
    pip install --no-cache-dir -r requirements.txt

# Start fresh with minimal image
FROM python:3.12-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Create data directory with proper permissions
RUN mkdir -p /app/data && chmod 777 /app/data

# Set environment variables for memory optimization
ENV PYTHONPATH="/app" \
    PYTHONUNBUFFERED=1 \
    PYTHONMALLOC=malloc \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PYTHONOPTIMIZE=2 \
    MPLBACKEND=Agg \
    NUMBA_CACHE_DIR=/tmp/numba_cache \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    VECLIB_MAXIMUM_THREADS=1 \
    MEMORY_LIMIT="96M" \
    UVICORN_WORKERS=1 \
    UVICORN_MEMORY_MAX="80" \
    UVICORN_LOOP="uvloop" \
    UVICORN_HTTP="httptools"

EXPOSE 8000

# Run with strict memory constraints and optimized settings
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "1", "--limit-memory-hard", "80", "--limit-memory-soft", "64", \
     "--timeout-keep-alive", "5", "--no-access-log", "--loop", "uvloop", \
     "--http", "httptools"]
