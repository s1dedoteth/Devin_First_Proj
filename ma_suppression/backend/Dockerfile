FROM alpine:3.18 AS builder

# Install build dependencies
RUN apk add --no-cache \
    pypy3-dev \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    && ln -sf /usr/bin/pypy3 /usr/local/bin/python

WORKDIR /app

# Set up virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install minimal dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir wheel && \
    # Install core dependencies only
    pip install --no-cache-dir fastapi==0.104.1 uvicorn==0.24.0 sqlalchemy==2.0.23 && \
    # Install other dependencies with minimal features
    pip install --no-cache-dir -r requirements.txt --no-deps

# Start fresh with minimal image
FROM alpine:3.18

# Install runtime dependencies only
RUN apk add --no-cache \
    pypy3 \
    tzdata \
    && ln -sf /usr/bin/pypy3 /usr/local/bin/python

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set environment variables for minimal memory usage
ENV PYTHONPATH="/app" \
    PYTHONUNBUFFERED=1 \
    PYTHONMALLOC=malloc \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PYTHONOPTIMIZE=2 \
    MEMORY_LIMIT="32M" \
    MPLBACKEND=Agg \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    VECLIB_MAXIMUM_THREADS=1 \
    UVICORN_WORKERS=1 \
    UVICORN_MEMORY_MAX="24" \
    UVICORN_LOOP="uvloop" \
    UVICORN_HTTP="httptools"

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
    MEMORY_LIMIT="64M" \
    UVICORN_WORKERS=1 \
    UVICORN_MEMORY_MAX="48" \
    UVICORN_LOOP="uvloop" \
    UVICORN_HTTP="httptools"

EXPOSE 8000

# Run with strict memory constraints and optimized settings
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "1", "--limit-memory-hard", "48", "--limit-memory-soft", "32", \
     "--timeout-keep-alive", "5", "--no-access-log", "--loop", "uvloop", \
     "--http", "httptools"]
