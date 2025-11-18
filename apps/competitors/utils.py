import requests
from math import radians, cos, sin, asin, sqrt
from django.conf import settings

from apps.competitors.competitor_categories.models import CompetitorCategory

FOURSQUARE_API_KEY = settings.FOURSQUARE_API_KEY
API_VERSION_HEADER = "2025-06-17"
FOURSQUARE_API_URL = "https://places-api.foursquare.com/places/search"


def haversine(lat1, lon1, lat2, lon2):
    """2 nuqta orasidagi masofani km da hisoblaydi."""
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
    """Lat/Lon O‘zbekiston chegarasida joylashganmi — True/False"""
    return 37.0 <= lat <= 46.0 and 56.0 <= lon <= 74.0


def geocode_nominatim(address: str):
    """OSM Nominatim orqali geokodlash"""
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
    """
    Foursquare dan joylarni olib, faqat O‘zbekiston ichidagilarni qaytaradi
    """
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

        # Koordinatalarni olish: location.lat/lng yoki geocodes.main
        lat = location.get("lat") or location.get("geocodes", {}).get("main", {}).get("latitude")
        lon = location.get("lng") or location.get("geocodes", {}).get("main", {}).get("longitude")
        address = location.get("formatted_address")

        if not address:
            continue

        # Agar koordinata bo'lmasa — Nominatim orqali aniqlaymiz
        if not lat or not lon:
            lat, lon = geocode_nominatim(address)

        # Faqat O‘zbekiston ichidagi joylar qabul qilinadi
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




#
# import requests
#
# from math import radians, cos, sin, asin, sqrt
# from django.conf import settings
#
#
# from apps.competitors.competitor_categories.models import CompetitorCategory
#
# FOURSQUARE_API_KEY = settings.FOURSQUARE_API_KEY
# YANDEX_GEOCODE_KEY=settings.YANDEX_GEOCODE_KEY
#
# API_VERSION_HEADER = "2025-06-17"
# FOURSQUARE_API_URL = "https://places-api.foursquare.com/places/search"
# YANDEX_GEO_URL = "https://geocode-maps.yandex.ru/1.x/"
#
#
# def haversine(lat1, lon1, lat2, lon2):
#     """2 nuqta orasidagi masofani km da hisoblaydi."""
#     R = 6371
#     if not all([lat1, lon1, lat2, lon2]):
#         return 9999
#     lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
#     d_lat = lat2 - lat1
#     d_lon = lon2 - lon1
#     a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
#     c = 2 * asin(sqrt(a))
#     return R * c
#
#
# def is_inside_uzbekistan(lat, lon):
#     """Lat/Lon O‘zbekiston chegarasida joylashganmi — True/False"""
#     return 37.0 <= lat <= 46.0 and 56.0 <= lon <= 74.0
#
#
# # def geocode_yandex(address: str):
# #     """Yandex orqali geokodlash"""
# #     if not address:
# #         return None, None
# #
# #     try:
# #         resp = requests.get(YANDEX_GEO_URL, params={
# #             "apikey": YANDEX_GEOCODE_KEY,
# #             "geocode": address,
# #             "format": "json",
# #             "results": 1
# #         }, timeout=10)
# #         data = resp.json()
# #         feature_member = data.get("response", {}).get("GeoObjectCollection", {}).get("featureMember", [])
# #         if feature_member:
# #             lon, lat = feature_member[0]["GeoObject"]["Point"]["pos"].split()
# #             return float(lat), float(lon)
# #     except Exception as e:
# #         print(f"[Geocode Error] {address}: {e}")
# #
# #     return None, None
#
#
# def geocode_osm(address: str):
#     import requests
#     try:
#         resp = requests.get(
#             "https://nominatim.openstreetmap.org/search",
#             params={"q": address, "format": "json", "limit": 1},
#             headers={"User-Agent": "get_place_app"}
#         )
#         data = resp.json()
#         if data:
#             return float(data[0]["lat"]), float(data[0]["lon"])
#     except Exception as e:
#         print(f"[OSM Geocode Error] {address}: {e}")
#     return None, None
#
#
# def search_places_with_geocode(query: str, category_name: str):
#     """
#     Foursquare dan joylarni olib, faqat O‘zbekiston ichidagilarni qaytaradi
#     """
#     if not query or not category_name:
#         return []
#
#     category = CompetitorCategory.objects.filter(name_uz=category_name).first()
#     if not category:
#         print(f"[Category Not Found] {category_name}")
#         return []
#
#     headers = {
#         "Accept": "application/json",
#         "Authorization": f"Bearer {FOURSQUARE_API_KEY}",
#         "X-Places-API-Version": API_VERSION_HEADER,
#     }
#
#     params = {
#         "near": query,
#         "query": category_name,
#         "limit": 50
#     }
#
#     try:
#         resp = requests.get(FOURSQUARE_API_URL, headers=headers, params=params, timeout=10)
#         resp.raise_for_status()
#         data = resp.json()
#     except Exception as e:
#         print(f"[Foursquare API Error] {query}, {category_name}: {e}")
#         return []
#
#     results = []
#     for place in data.get("results", []):
#         name = place.get("name", "Unknown")
#         location = place.get("location", {})
#         address = location.get("formatted_address")
#         if not address:
#             continue
#
#         lat = location.get("lat")
#         lon = location.get("lng")
#
#         # Agar koordinata bo'lmasa — Yandex orqali aniqlaymiz
#         if not lat or not lon:
#             lat, lon = geocode_osm(address)
#
#         #Faqat O‘zbekiston ichidagi joylar qabul qilinadi
#         if not (lat and lon and is_inside_uzbekistan(lat, lon)):
#             print(f"[Outside Uzbekistan] {name} — {address}")
#             continue
#
#         results.append({
#             "name_uz": name,
#             "address": address,
#             "latitude": lat,
#             "longitude": lon,
#             "category": category,
#         })
#
#     return results
