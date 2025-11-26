import requests
from math import radians, cos, sin, asin, sqrt
from django.conf import settings

from apps.competitors.competitor_categories.models import CompetitorCategory

FOURSQUARE_API_KEY = settings.FOURSQUARE_API_KEY
API_VERSION_HEADER = "2025-06-17"
FOURSQUARE_API_URL = "https://places-api.foursquare.com/places/search"


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    if not all([lat1, lon1, lat2, lon2]):
        return 9999
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    d_lat = lat2 - lat1
    d_lon = lon2 - lon1
    a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


def is_inside_uzbekistan(lat, lon):
    return 37.0 <= lat <= 46.0 and 56.0 <= lon <= 74.0


def geocode_nominatim(address: str):
    if not address:
        return None, None

    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": address, "format": "json", "limit": 1},
            headers={"User-Agent": "get_place_app"},
            timeout=10
        )
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"[Nominatim Error] {address}: {e}")

    return None, None


def search_places_with_geocode(query: str, category_name: str):
    if not query or not category_name:
        return []

    category = CompetitorCategory.objects.filter(name_uz=category_name).first()
    if not category:
        print(f"[Category Not Found] {category_name}")
        return []

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {FOURSQUARE_API_KEY}",
        "X-Places-API-Version": API_VERSION_HEADER,
    }

    params = {
        "near": query,
        "query": category_name,
        "limit": 50
    }

    try:
        resp = requests.get(FOURSQUARE_API_URL, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[Foursquare API Error] {query}, {category_name}: {e}")
        return []

    results = []
    for place in data.get("results", []):
        name = place.get("name", "Unknown")
        location = place.get("location", {})

        lat = location.get("lat") or location.get("geocodes", {}).get("main", {}).get("latitude")
        lon = location.get("lng") or location.get("geocodes", {}).get("main", {}).get("longitude")
        address = location.get("formatted_address")

        if not address:
            continue

        if not lat or not lon:
            lat, lon = geocode_nominatim(address)

        if not (lat and lon and is_inside_uzbekistan(lat, lon)):
            print(f"[Outside Uzbekistan / Missing coords] {name} — {address} | lat={lat}, lon={lon}")
            continue

        results.append({
            "name_uz": name,
            "address": address,
            "latitude": lat,
            "longitude": lon,
            "category": category,
        })

    return results
