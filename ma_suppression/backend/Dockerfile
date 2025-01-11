FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    gcc \
    g++ \
    make \
    libc-dev \
    musl-dev \
    cargo \
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

# Copy application code
COPY . .

# Set environment variables for memory optimization
ENV PORT="8000" \
    PYTHONPATH="/app" \
    PYTHONUNBUFFERED=1 \
    PYTHONMALLOC=malloc \
    PYTHONDEVMODE=1 \
    WORKERS_PER_CORE="1" \
    MAX_WORKERS="1" \
    WEB_CONCURRENCY="1" \
    MEMORY_LIMIT="128M" \
    UVICORN_WORKERS=1 \
    UVICORN_MEMORY_MAX="128" \
    PYTHONWARNINGS="ignore"

# Create data directory with proper permissions
RUN mkdir -p /app/data && chmod 777 /app/data

# Expose port
EXPOSE 8000

# Run with memory constraints and optimized settings
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--limit-memory-hard", "128", "--timeout-keep-alive", "30", "--no-access-log"]
