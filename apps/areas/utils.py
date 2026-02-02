import requests
from django.conf import settings

YANDEX_GEOCODER_URL = "https://geocode-maps.yandex.ru/1.x/"


def save(self, *args, **kwargs):
<<<<<<< HEAD
    # Agar latitude/longitude bo‘sh bo‘lsa — manzildan aniqlaymiz
=======
    # Agar latitude/longitude bo‘sh bo‘lsa —
>>>>>>> 7cb6155 (Initial clean commit)
    if not self.latitude or not self.longitude:
        address = f"{self.street} {self.house_number or ''}"
        lat, lon = self.get_coordinates_from_address(address)
        if lat and lon:
            self.latitude = lat
            self.longitude = lon
    super().save(*args, **kwargs)

def get_coordinates_from_address(address):
    """
<<<<<<< HEAD
    Manzildan koordinata olish (Geocoding)
=======
    getting koordinates from address(Geocoding)
>>>>>>> 7cb6155 (Initial clean commit)
    """
    params = {
        "apikey": settings.YANDEX_API_KEY,
        "geocode": address,
        "format": "json",
    }
    response = requests.get(YANDEX_GEOCODER_URL, params=params)
    data = response.json()

    try:
        pos = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        lon, lat = pos.split(" ")
        return float(lat), float(lon)
    except (KeyError, IndexError):
        return None, None
