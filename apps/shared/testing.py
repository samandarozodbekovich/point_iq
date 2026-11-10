"""Helpers shared by the tests in every app's tests/ package."""
import json
from pathlib import Path

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry

# Throttles keep counters in the cache; tests use a local one instead of Redis.
LOCMEM_CACHE = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

DISTRICTS_DIR = Path(settings.BASE_DIR) / "data" / "districts"


def district_geometry(filename):
    """The (Multi)Polygon of a district GeoJSON file in data/districts."""
    data = json.loads((DISTRICTS_DIR / filename).read_text(encoding="utf-8"))
    feature = next(f for f in data["features"] if f["geometry"]["type"] in ("Polygon", "MultiPolygon"))
    return GEOSGeometry(json.dumps(feature["geometry"]), srid=4326)
