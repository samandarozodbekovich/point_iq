from celery import shared_task

from apps.ai.logger import logger
from ..utils.fetch_tashkent_data import get_fetch_data

@shared_task(bind=True, max_retries=3)
def fetch_tashkent_data(self, lat, lng, radius):
    try:
        result = get_fetch_data(lat, lng, radius)
        return result
    except Exception as e:
        logger.error(f"Google task error {e}")
        return self.retry(exc=e, countdown=60)

