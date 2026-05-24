# syntax=docker/dockerfile:1
FROM python:3.13-slim

WORKDIR /app

# Install system deps (optional but recommended)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 🔥 Force rebuild (dummy line)
RUN echo "rebuild-boto-20260524"

# Copy project
COPY . .

# Install Python deps
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
