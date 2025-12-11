import time
import logging
import requests
from django.conf import settings
from django.db import transaction
from apps.competitors.competitor.models import Competitor
from apps.competitors.competitor_categories.models import CompetitorCategory
from apps.competitors.utils.geocode_nominatim import geocode_nominatim, is_inside_uzbekistan

logger = logging.getLogger(__name__)

TWO_GIS_API_KEY = settings.TWO_GIS_API_KEY
CITY_ID = "70030076171122914"  # Tashkent
PAGE_SIZE = 10  # production key bilan 50 yoki 100


def safe_get_schedule(item, weekday="Mon"):
    """2GIS item'dan ish vaqti olish"""
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
    """
    2GIS'dan kelayotgan nomdan business nomini chiqarish

    Misol: "Evos, кафе быстрого питания" → "Evos"
    Misol: "KFC, ресторан быстрого питания" → "KFC"
    """
    org = item.get("org") or {}
    # Birinchi: org.primary bo'lsa (qisqa nomi)
    primary_name = org.get("primary", "").strip()
    if primary_name:
        return primary_name

    # Agar yo'q bo'lsa, toliq nomdan verguldan oldingi qismini olish
    name = item.get("name", "").strip()
    if "," in name:
        return name.split(",")[0].strip()

    return name if name else None


def find_category_by_purpose(purpose_name):
    """
    2GIS'dan kelayotgan purpose_name dan database'dagi category'ni topish

    Qidirish tartib:
    1. "Кафе, бар" → "Кафе" (verguldan oldingi qism)
    2. "кафе быстрого питания" → "кафе" (birinchi so'z)
    3. "ресторан быстрого питания" → "ресторан" (birinchi so'z)

    Misol natija:
    - "Кафе, бар" → CompetitorCategory.name_ru="Кафе"
    - "кафе быстрого питания" → CompetitorCategory.name_ru="Кафе"
    - "ресторан быстрого питания" → CompetitorCategory.name_ru="Ресторан"
    """
    if not purpose_name:
        return None

    purpose_name = purpose_name.strip()

    # 1. purpose_name'dan verguldan oldingi qismini olish
    # "Кафе, бар" → "Кафе"
    primary_purpose = purpose_name.split(",")[0].strip()

    # 2. Birinchi so'zni capitalize qilish (lowercase → Capitalized)
    # "кафе быстрого питания" → "Кафе быстрого питания" → first word = "Кафе"
    words = primary_purpose.split()
    if words:
        first_word = words[0]
        # Capitalize: "кафе" → "Кафе"
        first_word_capitalized = first_word[0].upper() + first_word[1:] if len(first_word) > 0 else first_word
    else:
        first_word_capitalized = primary_purpose

    # Database'da qidiruv - EXACT match (birinchi try)
    category = CompetitorCategory.objects.filter(
        name_ru__iexact=primary_purpose
    ).first()

    # Agar exact match bo'lmasa, capitalized versiyani qidirish
    if not category and primary_purpose != first_word_capitalized:
        category = CompetitorCategory.objects.filter(
            name_ru__iexact=first_word_capitalized
        ).first()

    # Agar hali yo'q bo'lsa, CONTAINS qidirish (fuzzy match)
    if not category:
        category = CompetitorCategory.objects.filter(
            name_ru__icontains=first_word_capitalized
        ).first()

    if not category:
        logger.warning(
            f"Category topilmadi: purpose_name='{purpose_name}', "
            f"primary='{primary_purpose}', first_word='{first_word_capitalized}'"
        )
    else:
        logger.info(
            f"Category topildi: purpose_name='{purpose_name}' → name_ru='{category.name_ru}'"
        )

    return category


def search_place_2gis(query: str = None, category_name: str = None, fetch_details: bool = True):
    """
    2GIS API'dan competitor'lar qidiruv va database'ga saqlash

    Mantiq:
    1. User 'query' bo'yicha (city nomi, address) qidiradi
    2. API natijasidan kelayotgan 'purpose_name'dan category topiladi
    3. 'purpose_name' ni 'name_ru' ga tenglashtirish orqali category ID sini oladi
    4. Competitor'ga shu category ID'sini birikitadi

    Args:
        query: Qidiruv so'zi (city nomi, address, business nomi)
        category_name: Filtrlash uchun (opsional) - qidiruv natijalarini bu category ga filter qiladi
        fetch_details: Qo'shimcha ma'lumot olish

    Returns:
        int: Saqalgan yangi competitor'lar soni
    """
    if not query:
        logger.error("2GIS: 'query' talab qilinadi")
        return 0

    q_value = query
    base_url = "https://catalog.api.2gis.com/3.0/items"
    page = 1
    all_items = []

    # API'dan ma'lumot olish
    while True:
        params = {
            "q": q_value,
            "type": "branch",
            "city_id": CITY_ID,
            "page_size": PAGE_SIZE,
            "page": page,
            "key": TWO_GIS_API_KEY
        }
        try:
            resp = requests.get(base_url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.ConnectionError as e:
            logger.error(f"2GIS: Internet ulanish muammosi - {e}")
            raise  # Task qayta urinsin
        except requests.exceptions.Timeout:
            logger.error("2GIS: Request timeout")
            raise
        except Exception as e:
            logger.exception(f"2GIS API error: {e}")
            break

        items = data.get("result", {}).get("items", [])
        if not items:
            break

        all_items.extend(items)
        page += 1
        time.sleep(0.1)

    logger.info(f"2GIS: fetched {len(all_items)} items for query='{q_value}'")
    if not all_items:
        return 0

    # Database'dagi mavjud external_id'larni olish
    existing_ids = set(
        Competitor.objects.filter(
            external_id__in=[int(it.get("id")) for it in all_items if it.get("id")]
        ).values_list("external_id", flat=True)
    )

    bulk_to_create = []

    for item in all_items:
        try:
            item_id = item.get("id")
            if not item_id:
                continue

            external_id = int(item_id)

            # Agar allaqachon database'da bo'lsa, skip
            if external_id in existing_ids:
                continue

            # Qo'shimcha ma'lumot olish
            if fetch_details:
                details = fetch_item_details(
                    item_id,
                    fields=[
                        "items.point",
                        "items.address_name",
                        "items.schedule",
                        "items.org",
                        "items.contact_groups",
                        "items.rating"
                    ]
                )
                if details:
                    item = details[0]

            # Asosiy ma'lumotlar
            name = item.get("name")
            address = item.get("address_name") or item.get("full_name")
            point = item.get("point") or {}
            lat = point.get("lat")
            lon = point.get("lon")

            # Koordinata yo'q bo'lsa, geocoding qilish
            if not lat or not lon:
                lat, lon = geocode_nominatim(address)

            # Koordinata yoki Uzbekistan chegarasi tekshirish
            if not lat or not lon or not is_inside_uzbekistan(lat, lon):
                logger.warning(f"Skipping (invalid coords or outside UZ): {name}")
                continue

            # Ish vaqti
            sch_from, sch_to = safe_get_schedule(item, "Mon")

            # ⭐ CATEGORY - purpose_name'dan topish
            purpose_name = item.get("purpose_name", "").strip()
            org = item.get("org") or {}
            org_extension = org.get("extension", "") if org else ""
            org_extension = org_extension.strip()

            # Agar purpose_name bo'sh bo'lsa, org.extension dan foydalanish
            if not purpose_name and org_extension:
                purpose_name = org_extension

            category_obj = find_category_by_purpose(purpose_name)

            # Agar category topilmasa, skip
            if not category_obj:
                logger.warning(
                    f"Competitor skip qilindi (category topilmadi): "
                    f"name={name}, purpose_name={purpose_name}"
                )
                continue

            # Agar user category_name bergan bo'lsa, filtrlash
            if category_name and category_obj.name_ru != category_name:
                logger.debug(
                    f"Competitor skip qilindi (filter): "
                    f"{category_obj.name_ru} != {category_name}"
                )
                continue

            # ⭐ NAME
            business_name = extract_business_name(item)
            name_ru = item.get("name", "").strip()

            comp = Competitor(
                category=category_obj,  # ⭐ purpose_name'dan topilgan category
                address=address or "",
                external_id=external_id,
                name_uz=business_name,  # Business nomi (Evos, KFC, etc.)
                name_ru=name_ru,  # Toliq nom
                name_cyr=None,
                latitude=lat,
                longitude=lon,
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