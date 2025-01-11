FROM tiangolo/uvicorn-gunicorn-fastapi:python3.12

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV MODULE_NAME="app.main" \
    VARIABLE_NAME="app" \
    PORT="8000" \
    PYTHONPATH="/app" \
    WORKERS_PER_CORE="1" \
    MAX_WORKERS="4"

# Expose port
EXPOSE 8000
