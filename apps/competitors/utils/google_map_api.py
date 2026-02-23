import requests
from django.conf import settings

def fetch_places_from_api():
    url = "https://places.googleapis.com/v1/places:searchNearby"

    GOOGLE_MAP_API_KEY = settings.GOOGLE_MAP_API_KEY

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAP_API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName,places.rating,places.userRatingCount"
    }

    try:
        response = requests.request("GET", url=url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"request failed with {e}")
        return None
