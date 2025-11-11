# Python image
FROM python:3.13-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Project files
COPY . .

# Default command
CMD ["gunicorn", "get_place.wsgi:application", "--bind", "0.0.0.0:8000"]
