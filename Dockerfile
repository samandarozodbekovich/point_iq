# 3.12: Django 6 and pyproj 3.8 (requirements.txt) need Python >= 3.12,
# and it matches the version the project is developed and tested with.
FROM python:3.12-slim AS base

# System libraries (GDAL/GEOS/PROJ for GeoDjango, libpq for psycopg2)
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

# Disable these NumPy CPU features to avoid illegal-instruction crashes on older CPUs (space-separated)
ENV NPY_DISABLE_CPU_FEATURES="AVX512F AVX512_SKX AVX2 AVX SSE4_2 SSSE3 SSE3 SSE2 SSE" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Explicit GDAL/GEOS library paths for Django (Linux)
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/libgeos_c.so

COPY requirements.txt .

# numpy is pinned in requirements.txt. The old separate "numpy<2.0.0"
# install conflicts with geopandas/pandas, which need numpy>=2.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/staticfiles /app/media