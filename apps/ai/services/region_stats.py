from apps.ai.logger import logger
from apps.networks.models import CellTower

from apps.citizens.people_consume.models import PeopleConsume
from apps.citizens.people_education.models import PeopleEducation



<<<<<<< HEAD
def get_region_stats(region_coords=None, radius=0.2):
    """
    Region statistikasini olish

    Args:
        region_coords (tuple): (latitude, longitude)
        radius (float): Qidiruv radiusi (gradusda)

    Returns:
        dict: Region statsitikasi
    """
    try:
        if not region_coords:
            return {}

        lat, lon = region_coords

        # Tower'larni radiusda topish
=======
def get_region_stats(region_coord=None, radius=0.2):
    try:
        if not region_coord:
            return {}

        lat, lon = region_coord

>>>>>>> 7cb6155 (Initial clean commit)
        towers = CellTower.objects.filter(
            latitude__gte=lat - radius,
            latitude__lte=lat + radius,
            longitude__gte=lon - radius,
            longitude__lte=lon + radius
        )

        nearest = list(towers.values("id", "latitude", "longitude", "operator_name"))

        return {
<<<<<<< HEAD
            "coordinates": region_coords,
=======
            "coordinates": region_coord,
>>>>>>> 7cb6155 (Initial clean commit)
            "nearest_towers": nearest,
            "towers_count": len(nearest),
            "population": PeopleConsume.objects.count(),
            "education_centers": PeopleEducation.objects.count(),
<<<<<<< HEAD
            "competitors": 0,  # Bu ma'lumot kerak bo'lsa, Competitor modelidan ol
            "gov_bodies": 0,  # Bu ma'lumot kerak bo'lsa, GovernmentBody modelidan ol
        }
    except Exception as e:
        logger.error(f"get_region_stats xatosi: {str(e)}")
=======
            "competitors": 0,
            "gov_bodies": 0,
        }
    except Exception as e:
        logger.error(f"get_region_stats error: {str(e)}")
>>>>>>> 7cb6155 (Initial clean commit)
        return {}