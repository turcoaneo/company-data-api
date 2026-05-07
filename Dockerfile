# syntax=docker/dockerfile:1
FROM python:3.13-slim

WORKDIR /app

COPY . ./

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
