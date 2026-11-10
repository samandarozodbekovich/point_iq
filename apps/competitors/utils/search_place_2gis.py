import time
import logging
import requests
from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import transaction
from apps.competitors.competitor.models import Competitor
from apps.competitors.competitor_categories.models import CompetitorCategory
from apps.competitors.utils.geocode_nominatim import geocode_nominatim, is_inside_uzbekistan

logger = logging.getLogger(__name__)

TWO_GIS_API_KEY = settings.TWO_GIS_API_KEY
CITY_ID = "70030076171122914"
PAGE_SIZE = 10
# Upper bound on search pages per query. The loop used to run until an
# empty page came back, however many paid requests that took.
MAX_PAGES = 10
# Ask the search endpoint for these directly instead of one byid request
# per item.
SEARCH_FIELDS = "items.point,items.full_name,items.schedule,items.org,items.contact_groups,items.rating"


def safe_get_schedule(item, weekday="Mon"):
    schedule = item.get("schedule") or {}
    day = schedule.get(weekday) or {}
    working_hours = day.get("working_hours") or []

    if working_hours and isinstance(working_hours, list):
        first_slot = working_hours[0] or {}
        return first_slot.get("from"), first_slot.get("to")
    return None, None


def fetch_item_details(item_id, fields=None):
    """2GIS'dan qo'shimcha ma'lumot olish"""
    base = "https://catalog.api.2gis.com/3.0/items/byid"
    params = f"?id={item_id}&key={TWO_GIS_API_KEY}"
    if fields:
        params += f"&fields={','.join(fields)}"
    url = base + params
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json().get("result", {}).get("items", [])


def extract_business_name(item):

    org = item.get("org") or {}
    primary_name = org.get("primary", "").strip()
    if primary_name:
        return primary_name

    name = item.get("name", "").strip()
    if "," in name:
        return name.split(",")[0].strip()

    return name if name else None


def find_category_by_purpose(purpose_name):
    if not purpose_name:
        return None

    purpose_name = purpose_name.strip()
    primary_purpose = purpose_name.split(",")[0].strip()

    category = CompetitorCategory.objects.filter(name_ru__iexact=primary_purpose).first()

    if not category:
        words = primary_purpose.split()
        if words:
            first_word = words[0].capitalize()
            category = CompetitorCategory.objects.filter(name_ru__icontains=first_word).first()

    if not category:
        category, created = CompetitorCategory.objects.get_or_create(
            name_ru="Прочее",
            defaults={
                'name_uz': "Boshqa",
                'name_ru': "Прочее"
            }
        )
    return category


def search_place_2gis(query: str = None, category_name: str = None, fetch_details: bool = True):

    if not query:
        logger.error("2GIS: 'query' talab qilinadi")
        return 0

    q_value = query
    base_url = "https://catalog.api.2gis.com/3.0/items"
    page = 1
    all_items = []

    while True:
        params = {
            "q": q_value,
            "type": "branch",
            "city_id": CITY_ID,
            "page_size": PAGE_SIZE,
            "page": page,
            "fields": SEARCH_FIELDS,
            "key": TWO_GIS_API_KEY
        }
        try:
            resp = requests.get(base_url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.ConnectionError as e:
            logger.error(f"2GIS: Internet ulanish muammosi - {e}")
            raise
        except requests.exceptions.Timeout:
            logger.error("2GIS: Request timeout")
            raise
        except Exception as e:
            logger.exception(f"2GIS API error: {e}")
            break

        result = data.get("result", {})
        items = result.get("items", [])
        if not items:
            break

        all_items.extend(items)
        total = result.get("total")
        if (total is not None and len(all_items) >= total) or page >= MAX_PAGES:
            break
        page += 1
        time.sleep(0.1)

    logger.info(f"2GIS: fetched {len(all_items)} items for query='{q_value}'")
    if not all_items:
        return 0

    # external_id is a TextField: compare strings. Converting to int made
    # every "is it already saved?" check miss (123 != "123"), and an id
    # that wasn't a plain number crashed the whole import here.
    existing_ids = set(
        Competitor.objects.filter(
            external_id__in=[str(it.get("id")).strip() for it in all_items if it.get("id")]
        ).values_list("external_id", flat=True)
    )

    bulk_to_create = []

    for item in all_items:
        try:
            item_id = item.get("id")
            if not item_id:
                continue

            external_id = str(item_id).strip()

            if external_id in existing_ids:
                continue
            existing_ids.add(external_id)  # also skip repeats within this batch

            # Search already returned the details; fall back to byid only
            # when it came back without coordinates.
            if fetch_details and not item.get("point"):
                details = fetch_item_details(
                    item_id,
                    fields=[
                        "items.point",
                        "items.full_name",
                        "items.schedule",
                        "items.org",
                        "items.contact_groups",
                        "items.rating"
                    ]
                )
                if details:
                    item = details[0]

            name = item.get("name")
            address = item.get("full_name") or item.get("address_name")
            point = item.get("point") or {}
            lat = point.get("lat")
            lon = point.get("lon")

            if not lat or not lon:
                lat, lon = geocode_nominatim(address)

            if not lat or not lon or not is_inside_uzbekistan(lat, lon):
                logger.warning(f"Skipping (invalid coords or outside UZ): {name}")
                continue

            sch_from, sch_to = safe_get_schedule(item, "Mon")

            purpose_name = item.get("purpose_name", "").strip()
            org = item.get("org") or {}
            org_extension = org.get("extension", "") if org else ""
            org_extension = org_extension.strip()

            if not purpose_name and org_extension:
                purpose_name = org_extension

            category_obj = find_category_by_purpose(purpose_name)

            if not category_obj:
                logger.warning(
                    f"Competitor skip qilindi (category topilmadi): "
                    f"name={name}, purpose_name={purpose_name}"
                )
                continue

            if category_name and category_obj.name_ru != category_name:
                logger.debug(
                    f"Competitor skip qilindi (filter): "
                    f"{category_obj.name_ru} != {category_name}"
                )
                continue

            business_name = extract_business_name(item)
            name_ru = item.get("name", "").strip()

            comp = Competitor(
                category=category_obj,
                address=address or "",
                external_id=external_id,
                name_uz=business_name,
                name_ru=name_ru,
                name_cyr=None,
                latitude=lat,
                longitude=lon,
                location=Point(float(lon), float(lat), srid=4326),
                schedule_from=sch_from,
                schedule_to=sch_to,
            )
            bulk_to_create.append(comp)

        except Exception:
            logger.exception(f"Failed to parse item: {item}")
            continue

    created_count = 0
    if bulk_to_create:
        with transaction.atomic():
            Competitor.objects.bulk_create(bulk_to_create, ignore_conflicts=True)
            created_count = len(bulk_to_create)

    filter_msg = f", filtered by category='{category_name}'" if category_name else ""
    logger.info(f"2GIS: created {created_count} new competitors for query='{q_value}'{filter_msg}")
    return created_count