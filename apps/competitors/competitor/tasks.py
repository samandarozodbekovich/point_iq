from celery import shared_task
from .models import Competitor
from apps.competitors.competitor_categories.models import CompetitorCategory
from ..utils import search_places_with_geocode
from django.db import transaction



@shared_task(bind=True)
def bulk_create_or_update_competitors(self, payload):
    """
    Bulk create yoki update competitors
    """
    city = payload.get('city')
    category = payload.get('category')
    lang = payload.get('lang', 'uz')

    if not city or not category:
        return {'status': 'failed', 'error': 'city or category missing'}

    results = search_places_with_geocode(city, category)
    if not results:
        return {'status': 'success', 'created_count': 0, 'message': 'No results'}

    lookup_field = f'name_{lang}'

    # Category bazadan olish yoki yaratish
    category, _ = CompetitorCategory.objects.get_or_create(
        **{lookup_field: category},
        defaults={
            'name_uz': category if lang == 'uz' else None,
            'name_ru': category if lang == 'ru' else None,
            'name_uz_cyr': category if lang == 'uz_cyr' else None,
        }
    )

    existing = Competitor.objects.filter(
        **{f"{lookup_field}__in": [r.get(lookup_field) for r in results]},
        category=category
    ).in_bulk(field_name=lookup_field)

    competitors_to_create = []
    competitors_to_update = []

    total = len(results)
    for idx, data in enumerate(results, start=1):
        name_value = data.get(lookup_field)
        if not name_value:
            continue

        if name_value in existing:
            # Update mavjud competitor
            obj = existing[name_value]
            obj.address = data.get('address')
            obj.latitude = data.get('latitude')
            obj.longitude = data.get('longitude')
            obj.rating = data.get('rating')
            obj.footfall_estimate = data.get('footfall_estimate')
            obj.review_count = data.get('review_count')
            competitors_to_update.append(obj)
        else:
            # Create yangi competitor
            competitors_to_create.append(
                Competitor(
                    name_uz=data.get('name_uz'),
                    name_ru=data.get('name_ru'),
                    name_uz_cyr=data.get('name_uz_cyr'),
                    address=data.get('address'),
                    longitude=data.get('longitude'),
                    latitude=data.get('latitude'),
                    rating=data.get('rating'),
                    footfall_estimate=data.get('footfall_estimate'),
                    review_count=data.get('review_count'),
                    category=category
                )
            )

        self.update_state(state='PROGRESS', meta={'current': idx, 'total': total})

    with transaction.atomic():
        if competitors_to_create:
            Competitor.objects.bulk_create(competitors_to_create)
        if competitors_to_update:
            Competitor.objects.bulk_update(
                competitors_to_update,
                fields=[
                    'address', 'latitude', 'longitude', 'rating',
                    'footfall_estimate', 'review_count'
                ]
            )

    return {
        'status': 'success',
        'created_count': len(competitors_to_create),
        'updated_count': len(competitors_to_update)
    }


# apps/competitors/tasks.py


@shared_task
def fetch_and_update_competitors(city, category_name):
    """
    Tashqi API dan joylarni olib kelish va bazaga bulk_create / bulk_update bilan saqlash
    """
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
