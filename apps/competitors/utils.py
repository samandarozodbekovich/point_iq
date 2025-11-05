import requests
from django.conf import settings


FOURSQUARE_API_KEY = settings.FOURSQUARE_API_KEY
YANDEX_GEOCODE_KEY=settings.YANDEX_GEOCODE_KEY

API_VERSION_HEADER = "2025-06-17"
FOURSQUARE_API_URL = "https://places-api.foursquare.com/places/search"
GEO_URL = "https://geocode-maps.yandex.ru/1.x/"

CATEGORY_IDS = {
    "fast_food": "4bf58dd8d48988d16e941735",
    "gas_station": "4bf58dd8d48988d113951735",
    "auto_repair": "52f2ab2ebcbc57f1066b8b44",
    "barbershop": "63be6904847c3692a84b9b49",
    "hair_salon": "4bf58dd8d48988d110951735",
    "nail_salon": "4f04aa0c2fb6e1c99f3db0b8",
    "spa": "4bf58dd8d48988d1ed941735",
    "hospital": "4bf58dd8d48988d196941735",
    "museum": "4bf58dd8d48988d181941735",
    "art_museum": "4bf58dd8d48988d18f941735",
    "supermarket": "52f2ab2ebcbc57f1066b8b46",
    "atm": "52f2ab2ebcbc57f1066b8b56",
    "bank": "4bf58dd8d48988d10a951735",
    "hotel": "4bf58dd8d48988d1e0931735",
    "mall": "4bf58dd8d48988d1f1931735",
    "cafe": "4bf58dd8d48988d16d941735",
    "gym": "4f4528bc4b90abdf24c9de85",
}


def geocode_yandex(address):
    """Yandex orqali geokodlash"""
    params = {
        "apikey": YANDEX_GEOCODE_KEY,
        "geocode": address,
        "format": "json",
        "results": 1
    }
    try:
        resp = requests.get(GEO_URL, params=params, timeout=10)
        data = resp.json()
        feature_member = data["response"]["GeoObjectCollection"]["featureMember"]
        if feature_member:
            pos = feature_member[0]["GeoObject"]["Point"]["pos"]
            lon, lat = pos.split()
            return float(lat), float(lon)
    except Exception as e:
        print("Yandex geocode xatolik:", e)
    return None, None


def search_places_with_geocode(city="", category=""):
    """
    Foursquare dan faqat kerakli kategoriya bo'yicha joylarni olib,
    name, address, latitude, longitude, category bilan JSON qaytaradi
    """
    if not category or category not in CATEGORY_IDS:
        return []

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {FOURSQUARE_API_KEY}",
        "X-Places-API-Version": API_VERSION_HEADER,
    }

    params = {
        "near": city,
        "categories": CATEGORY_IDS[category],
        "limit": 50
    }

    response = requests.get(FOURSQUARE_API_URL, headers=headers, params=params)
    try:
        data = response.json()
    except Exception:
        data = {"results": []}

    results = []
    for place in data.get("results", []):
        address = place.get("location", {}).get("formatted_address")
        name = place.get("name", "Unknown")
        if not address:
            continue
        lat, lon = geocode_yandex(address)
        results.append({
            "name": name,
            "address": address,
            "latitude": lat,
            "longitude": lon,
            "category": category
        })

    return results