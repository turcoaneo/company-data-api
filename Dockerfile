# syntax=docker/dockerfile:1
FROM python:3.13-slim

WORKDIR /app

# Install system deps (optional but recommended)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . .

# Install Python deps
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI + Cron threads
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
