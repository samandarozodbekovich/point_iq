
from celery import shared_task
from .models import Competitor
from ..utils import search_places_with_geocode
from django.db import transaction


@shared_task
def fetch_and_update_competitors(city, category_name):
    places = search_places_with_geocode(city, category_name)
    if not places:
        print(f"[No results] {city}, {category_name}")
        return

    existing_map = {
        (c.name_uz, c.address): c
        for c in Competitor.objects.filter(category__name_uz=category_name)
    }

    new_objs, update_objs = [], []

    for item in places:
        key = (item["name_uz"], item["address"])
        if key in existing_map:
            comp = existing_map[key]
            comp.latitude = item["latitude"]
            comp.longitude = item["longitude"]
            update_objs.append(comp)
        else:
            new_objs.append(Competitor(**item))

    with transaction.atomic():
        if new_objs:
            Competitor.objects.bulk_create(new_objs, ignore_conflicts=True)
        if update_objs:
            Competitor.objects.bulk_update(update_objs, ["latitude", "longitude"])

    print(f"[Celery] {len(new_objs)} new, {len(update_objs)} updated for {city} - {category_name}")

