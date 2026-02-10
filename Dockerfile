
FROM python:3.11-slim AS base

# Tizim kutubxonalarini o'rnatish
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

# NumPy xatosini oldini olish uchun muhit o'zgaruvchilari
ENV NPY_DISABLE_CPU_FEATURES="AVX512F,AVX512_SKX,AVX2,AVX,SSE4_2,SSSE3,SSE3,SSE2,SSE" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .

# MUHIM: NumPy ning eskiroq va barqaror versiyasini majburan o'rnatamiz
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "numpy<2.0.0" && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/staticfiles /app/media
