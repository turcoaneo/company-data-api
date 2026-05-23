# syntax=docker/dockerfile:1
FROM python:3.13-slim

WORKDIR /app

# Install system deps (optional but recommended)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 🔥 Force rebuild (dummy line)
RUN echo "rebuild-port-80-20260523"

# Copy project
COPY . .

# Install Python deps
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 80

# Start FastAPI + Cron threads
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
