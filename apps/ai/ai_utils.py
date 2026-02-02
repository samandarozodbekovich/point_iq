import numpy as np

from apps.ai.services import logger
from apps.networks.models import CellTower
from apps.competitors.competitor.models import Competitor
from apps.citizens.people_consume.models import PeopleConsume
from apps.citizens.people_education.models import PeopleEducation
from apps.government_bodies.models import GovernmentBody

index = None
tower_ids = None
people_consume_data = None
people_education_data = None


<<<<<<< HEAD
def build_vector_db(region_coords=None, radius_km=20):
    """
    Vector database qurilishi - FAISS o'chirilgan, sodda versiya
    Tower ma'lumotlarini va statsitikalarni yig'ish

    Args:
        region_coords (tuple): (latitude, longitude)
        radius_km (float): Qidiruv radiusi (kilometrda)

    Returns:
        tuple: (tower_data, people_consume_data, people_education_data)
    """
    global tower_data, people_consume_data, people_education_data

    try:
        # Tower ma'lumotlarini olish
        towers = CellTower.objects.all()

        if region_coords:
            lat, lon = region_coords
=======
def build_vector_db(region_coord=None, radius_km=20):

    global tower_data, people_consume_data, people_education_data

    try:
        towers = CellTower.objects.all()

        if region_coord:
            lat, lon = region_coord
>>>>>>> 7cb6155 (Initial clean commit)
            # 0.2 degrees ≈ 20 km
            towers = towers.filter(
                latitude__gte=lat - 0.2,
                latitude__lte=lat + 0.2,
                longitude__gte=lon - 0.2,
                longitude__lte=lon + 0.2
            )

<<<<<<< HEAD
        # Tower'larni dictionary formatida saqlash
=======
>>>>>>> 7cb6155 (Initial clean commit)
        if towers.exists():
            tower_data = list(towers.values(
                "id",
                "latitude",
                "longitude",
                "operator_name"
            ))
            logger.info(f"Loaded {len(tower_data)} towers")
        else:
            tower_data = None
            logger.warning("No towers found in region")

<<<<<<< HEAD
        # Aholi istemolli ma'lumotlari
        people_consume_data = list(PeopleConsume.objects.all().values())
        logger.info(f"Loaded {len(people_consume_data)} consume records")

        # Ta'lim markazlari ma'lumotlari
=======
        people_consume_data = list(PeopleConsume.objects.all().values())
        logger.info(f"Loaded {len(people_consume_data)} consume records")

>>>>>>> 7cb6155 (Initial clean commit)
        people_education_data = list(PeopleEducation.objects.all().values())
        logger.info(f"Loaded {len(people_education_data)} education records")

        return tower_data, people_consume_data, people_education_data

    except Exception as e:
<<<<<<< HEAD
        logger.error(f"build_vector_db xatosi: {str(e)}")
        return None, None, None

def query_ai(user_query: str, region_coords=None, top_k=5):
=======
        logger.error(f"build_vector_db error: {str(e)}")
        return None, None, None

def query_ai(user_query: str, region_coord=None, top_k=5):
>>>>>>> 7cb6155 (Initial clean commit)

    global index, tower_ids, people_consume_data, people_education_data

    nearest_towers_info = []
<<<<<<< HEAD
    if index is not None and tower_ids and region_coords:
        vector = np.array([region_coords]).astype('float32')
        D, I = index.search(vector, top_k)
        nearest_ids = [tower_ids[i] for i in I[0]]
=======
    if index is not None and tower_ids and region_coord:
        vector = np.array([region_coord]).astype('float32')
        d, i = index.search(vector, top_k)
        nearest_ids = [tower_ids[i] for i in i[0]]
>>>>>>> 7cb6155 (Initial clean commit)
        nearest_towers_info = list(CellTower.objects.filter(id__in=nearest_ids).values(
            "id", "latitude", "longitude", "operator_name"
        ))
    else:
        nearest_ids = []

    response = {
        "query_received": user_query,
        "nearest_tower_ids": nearest_ids,
        "nearest_towers_info": nearest_towers_info,
        "vector_db_count": len(tower_ids) if tower_ids else 0,
        "citizens_total": len(people_consume_data),
        "education_records_total": len(people_education_data),
        "competitors_total": Competitor.objects.count(),
        "government_bodies_total": GovernmentBody.objects.count()
    }

    return response
