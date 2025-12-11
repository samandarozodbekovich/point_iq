import requests
from django.conf import settings
from apps.competitors.competitor_categories.models import CompetitorCategory
from apps.competitors.utils.geocode_nominatim import geocode_nominatim, is_inside_uzbekistan

FOURSQUARE_API_KEY = settings.FOURSQUARE_API_KEY
API_VERSION_HEADER = "2025-06-17"
FOURSQUARE_API_URL = "https://places-api.foursquare.com/places/search"


def search_places_with_geocode(query: str, category: str):
    if not query or not category:
        return []

    category = CompetitorCategory.objects.filter(name_uz=category).first()
    if not category:
        print(f"[Category Not Found] {category}")
        return []

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {FOURSQUARE_API_KEY}",
        "X-Places-API-Version": API_VERSION_HEADER
  # to‘g‘ri format
    }

    params = {
        "near": query,
        "query": category,
        "limit": 50
    }

    try:
        resp = requests.get(FOURSQUARE_API_URL, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[Foursquare API Error] {query}, {category}: {e}")
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

