from celery import shared_task
from apps.competitors.utils.search_place_2gis import search_place_2gis
from apps.ai.logger import logger


@shared_task(bind=True, max_retries=3)
def fetch_and_update_competitors_2gis(self, query, category_name):
    try:
        created = search_place_2gis(
            query=query,
            category_name=category_name,
            fetch_details=True
        )
        logger.info(
            f"[2GIS Task] completed: query={query}, category={category_name}, created={created}"
        )
        return {"status": "success", "created": created}

    except Exception as e:
        logger.exception(
            f"[2GIS Task] failed: query={query}, category={category_name}, error={e}"
        )
        # 3 marta qayta urinish
        raise self.retry(exc=e, countdown=60)

