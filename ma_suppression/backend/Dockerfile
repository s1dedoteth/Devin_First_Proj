FROM python:3.12-slim

WORKDIR /app

# Install system dependencies and Python packages in a single layer
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies system-wide
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir aiohttp==3.9.1

# Copy application code
COPY . .

# Set Python path and ensure no virtualenv is active
ENV PYTHONPATH=/app \
    VIRTUAL_ENV="" \
    PATH="/usr/local/bin:$PATH"

EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
