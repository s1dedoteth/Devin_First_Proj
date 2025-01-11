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

# Set environment variables
ENV PORT="8000" \
    PYTHONPATH="/app" \
    PYTHONUNBUFFERED=1 \
    WORKERS_PER_CORE="1" \
    MAX_WORKERS="1" \
    WEB_CONCURRENCY="1" \
    MEMORY_LIMIT="256M"

# Expose port
EXPOSE 8000

# Run the application with memory constraints
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--limit-memory-hard", "256"]
