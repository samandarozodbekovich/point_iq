import requests
import time

def is_inside_uzbekistan(lat, lon):

    return 37.0 <= lat <= 46.0 and 56.0 <= lon <= 74.0

def geocode_nominatim(address: str):
    """Nominatim orqali address geocoding"""
    if not address:
        return None, None

    for _ in range(3):  # 3 marta urinish
        try:
            resp = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": address, "format": "json", "limit": 1},
                headers={"User-Agent": "get_place_app"},
                timeout=10
            )
            data = resp.json()
            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                if is_inside_uzbekistan(lat, lon):
                    return lat, lon
        except Exception as e:
            print(f"[Nominatim Error] {address}: {e}")
        time.sleep(1)

    return None, None
