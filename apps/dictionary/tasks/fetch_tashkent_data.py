import requests
from celery import shared_task
from django.core.cache import cache

from apps.ai.logger import logger
from ..utils.fetch_tashkent_data import area_cache_key, fetch_overpass, save_elements

# Long enough to cover every retry below (60 + 120 + 240 s plus timeouts).
PENDING_TTL = 15 * 60
# An area fetched once is not fetched again for a day, even if it was empty.
DONE_TTL = 24 * 60 * 60


@shared_task(bind=True, max_retries=3)
def fetch_tashkent_data(self, lat, lng, radius):
    pending_key = area_cache_key("pending", lat, lng, radius)

    try:
        data = fetch_overpass(lat, lng, radius)
    except (requests.RequestException, ValueError) as e:
        # Network, HTTP or bad-JSON errors may pass on their own: retry with backoff.
        if self.request.retries >= self.max_retries:
            cache.delete(pending_key)
            raise
        logger.warning(f"Overpass fetch failed, retrying: {e}")
        raise self.retry(exc=e, countdown=60 * 2 ** self.request.retries)

    # Saving is not retried: a bug here fails the same way every time and a
    # retry would only send Overpass the same query again. The pending key
    # stays until it expires, so the view doesn't queue a new task meanwhile.
    counts = save_elements(data)

    cache.set(area_cache_key("done", lat, lng, radius), True, timeout=DONE_TTL)
    cache.delete(pending_key)
    return counts
