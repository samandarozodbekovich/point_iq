# apps/competitors/tasks.py
from celery import shared_task

from apps.areas.places.models import Place
from apps.areas.utils import get_coordinates_from_address
from apps.competitors.competitor.models import Competitor
from apps.competitors.competitor_categories.models import CompetitorCategory

@shared_task
def save_competitor_with_geocode(result):
    """
    Celery task: lat/lon bo'lmagan natijani keyinchalik saqlash
    result = {
        "name": "Bon!",
        "address": "Chimkent St 21, Toshkent, Toshkent Shahri",
        "latitude": None,
        "longitude": None,
        "category": "Coffee Shop"
    }
    """
    from apps.competitors.utils import geocode_yandex

    lat, lon = geocode_yandex(result["address"])
    if not lat or not lon:
        return None  # koordinata topilmasa hech narsa qilmaymiz

    result["latitude"] = lat
    result["longitude"] = lon
    save_competitor_direct(result)


def save_competitor_direct(result):
    """
    Natijani darhol bazaga saqlash
    """
    # Soddalashtirilgan variant: faqat Place va Competitor
    if not result.get("latitude") or not result.get("longitude"):
        return None

    # Place
    place, _ = Place.objects.get_or_create(
        house_number="",
        street=None,
        defaults={
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "description": result.get("address") or result.get("name")
        }
    )

    # Competitor
    category_name = result.get("category") or "Unknown"
    category, _ = CompetitorCategory.objects.get_or_create(name=category_name)
    competitor, _ = Competitor.objects.get_or_create(
        name_uz=result.get("name"),
        place=place,
        defaults={"category": category}
    )

    return competitor



@shared_task
def update_place_coordinates(place_id):
    try:
        place = Place.objects.get(id=place_id)
    except Place.DoesNotExist:
        return

    lat, lon = get_coordinates_from_address(place.address)
    if lat and lon:
        place.latitude = lat
        place.longitude = lon
        place.save()


@shared_task
def fetch_coordinates_task(place_id, address):
    lat, lon = get_coordinates_from_address(address)
    try:
        place = Place.objects.get(id=place_id)
        place.latitude = lat
        place.longitude = lon
        place.save()
    except Place.DoesNotExist:
        pass