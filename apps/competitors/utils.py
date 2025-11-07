import requests
from django.conf import settings

from apps.competitors.competitor_categories.models import CompetitorCategory

FOURSQUARE_API_KEY = settings.FOURSQUARE_API_KEY
YANDEX_GEOCODE_KEY=settings.YANDEX_GEOCODE_KEY

API_VERSION_HEADER = "2025-06-17"
FOURSQUARE_API_URL = "https://places-api.foursquare.com/places/search"
YANDEX_GEO_URL = "https://geocode-maps.yandex.ru/1.x/"

def geocode_yandex(address: str):
    """Yandex orqali geokodlash"""
    if not address:
        return None, None

    try:
        resp = requests.get(YANDEX_GEO_URL, params={
            "apikey": YANDEX_GEOCODE_KEY,
            "geocode": address,
            "format": "json",
            "results": 1
        }, timeout=10)
        data = resp.json()
        feature_member = data.get("response", {}).get("GeoObjectCollection", {}).get("featureMember", [])
        if feature_member:
            lon, lat = feature_member[0]["GeoObject"]["Point"]["pos"].split()
            return float(lat), float(lon)
    except Exception as e:
        print(f"[Geocode Error] {address}: {e}")

    return None, None


def search_places_with_geocode(city: str, category_name: str):
    """
    Foursquare dan joylarni olib, Yandex geokodlash bilan koordinatalarni qo‘shadi
    """
    if not city or not category_name:
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
        "near": city,
        "query": category_name,
        "limit": 50
    }

    try:
        resp = requests.get(FOURSQUARE_API_URL, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[Foursquare API Error] {city}, {category_name}: {e}")
        return []

    results = []
    for place in data.get("results", []):
        name = place.get("name", "Unknown")
        location = place.get("location", {})
        address = location.get("formatted_address")
        if not address:
            continue

        lat = location.get("lat")
        lon = location.get("lng")

        # Agar Foursquare koordinata bermagan bo‘lsa — Yandex orqali topamiz
        if not lat or not lon:
            lat, lon = geocode_yandex(address)

        results.append({
            "name_uz": name,
            "address": address,
            "latitude": lat,
            "longitude": lon,
            "category": category,
        })

    return results







# CATEGORY_IDS = {
#     "fast_food": "4bf58dd8d48988d16e941735",
#     "gas_station": "4bf58dd8d48988d113951735",
#     "auto_repair": "52f2ab2ebcbc57f1066b8b44",
#     "barbershop": "63be6904847c3692a84b9b49",
#     "hair_salon": "4bf58dd8d48988d110951735",
#     "nail_salon": "4f04aa0c2fb6e1c99f3db0b8",
#     "spa": "4bf58dd8d48988d1ed941735",
#     "hospital": "4bf58dd8d48988d196941735",
#     "museum": "4bf58dd8d48988d181941735",
#     "art_museum": "4bf58dd8d48988d18f941735",
#     "supermarket": "52f2ab2ebcbc57f1066b8b46",
#     "atm": "52f2ab2ebcbc57f1066b8b56",
#     "bank": "4bf58dd8d48988d10a951735",
#     "hotel": "4bf58dd8d48988d1e0931735",
#     "mall": "4bf58dd8d48988d1f1931735",
#     "cafe": "4bf58dd8d48988d16d941735",
#     "gym": "4f4528bc4b90abdf24c9de85",
# }