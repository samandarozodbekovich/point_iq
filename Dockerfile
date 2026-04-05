FROM python:3.11-slim AS base

# Tizim kutubxonalarini o'rnatish
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    cmake \
    libpq-dev \
    gcc \
    binutils \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# NumPy xatosini oldini olish uchun (bo'sh joy bilan ajratilgan formatda)
ENV NPY_DISABLE_CPU_FEATURES="AVX512F AVX512_SKX AVX2 AVX SSE4_2 SSSE3 SSE3 SSE2 SSE" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Django GDAL yo'llarini aniq ko'rsatish (Linux uchun)
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/libgeos_c.so

COPY requirements.txt .

# Avval pip ni yangilaymiz, keyin muammoli NumPy-ni o'rnatamiz, keyin qolganlarini
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "numpy<2.0.0" && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/staticfiles /app/media