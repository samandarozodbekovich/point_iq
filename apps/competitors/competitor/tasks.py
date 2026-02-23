from celery import shared_task
from apps.competitors.competitor.services import fetch_and_save_nearby_competitors
from apps.competitors.utils.search_place_2gis import search_place_2gis
from apps.ai.logger import logger

@shared_task(bind=True, max_retries=2)
def fetch_google_competitors_task(self, lat, lng, radius, category_id):
    try:
        result = fetch_and_save_nearby_competitors(lat, lng, radius, category_id)
        return result
    except Exception as e:
        logger.error(f"Google Task Error: {e}")
        raise self.retry(exc=e, countdown=60)

@shared_task(bind=True, max_retries=3)
def fetch_and_update_competitors_2gis(self, query, category_name):
    try:
        created = search_place_2gis(
            query=query,
            category_name=category_name,
            fetch_details=True
        )
        logger.info(f"[2GIS Task] completed: query={query}, created={created}")
        return {"status": "success", "created": created}
    except Exception as e:
        logger.exception(f"[2GIS Task] failed: {e}")
        raise self.retry(exc=e, countdown=60)
