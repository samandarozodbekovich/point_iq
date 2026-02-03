FROM python:3.13-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    cmake \
    libpq-dev \
    gcc \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/staticfiles /app/media

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1