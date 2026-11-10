import requests
from django.conf import settings
from django.db import transaction

from apps.competitors.competitor.models import Competitor
from apps.competitors.competitor_categories.models import CompetitorCategory


def get_nearby_places_new(lat, lng, radius, place_type):
    api_key = settings.GOOGLE_MAP_API_KEY
    url = "https://places.googleapis.com/v1/places:searchNearby"

    headers = {
        'Content-type': 'application/json',
        'X-Goog-Api-Key': api_key,
        "X-Goog-FieldMask": "places.name,places.displayName,places.formattedAddress,places.types,places.location,places.rating,places.userRatingCount"
    }

    data = {
        "includedTypes": [place_type] if isinstance(place_type, str) else place_type,
        "maxResultCount": 20,
        "rankPreference": "DISTANCE",
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": float(radius)
            }
        }
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    return {"error": response.text}


def fetch_and_save_nearby_competitors(lat, long, radius, category_id):
    try:
        category_obj = CompetitorCategory.objects.get(id=category_id)
        google_type = category_obj.google_type
    except CompetitorCategory.DoesNotExist:
        return {"error": "Competitor Category does not exist"}

    # Without a type Google gets includedTypes=[None]: a paid call that
    # can't return anything useful.
    if not google_type:
        return {"error": "This category has no google_type set"}

    raw_data = get_nearby_places_new(lat, long, radius, google_type)
    if "error" in raw_data:
        return raw_data

    places = raw_data.get('places', [])
    created_count = 0

    with transaction.atomic():
        for place in places:
            # In the new Google Places API the unique id is in 'name' (places/ChIJ...)
            g_id = place.get('name')

            print(f"Checking: {place.get('displayName', {}).get('text')} | ID: {g_id}")

            if not g_id:
                print("No ID, skipped.")
                continue

            try:
                obj, created = Competitor.objects.update_or_create(
                    google_place_id=g_id,
                    defaults={
                        "category": category_obj,
                        "name_uz": place.get("displayName", {}).get("text"),
                        "address": place.get("formattedAddress")[:120] if place.get("formattedAddress") else "",
                        "latitude": place.get("location", {}).get("latitude"),
                        "longitude": place.get("location", {}).get("longitude"),
                        "average_rating": place.get("rating"),
                        "review_count": place.get("userRatingCount", 0),
                    }
                )
                print(f"Saved, ID: {obj.id}")
                if created:
                    created_count += 1
            except Exception as e:
                print(f"Failed to save: {e}")

    return {
        "total_found": len(places),
        "created_count": created_count,
        "category_name": category_obj.name_uz,
        "data": raw_data
    }