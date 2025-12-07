from apps.ai.logger import logger
from apps.networks.models import CellTower

from apps.citizens.people_consume.models import PeopleConsume
from apps.citizens.people_education.models import PeopleEducation



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
        towers = CellTower.objects.filter(
            latitude__gte=lat - radius,
            latitude__lte=lat + radius,
            longitude__gte=lon - radius,
            longitude__lte=lon + radius
        )

        nearest = list(towers.values("id", "latitude", "longitude", "operator_name"))

        return {
            "coordinates": region_coords,
            "nearest_towers": nearest,
            "towers_count": len(nearest),
            "population": PeopleConsume.objects.count(),
            "education_centers": PeopleEducation.objects.count(),
            "competitors": 0,  # Bu ma'lumot kerak bo'lsa, Competitor modelidan ol
            "gov_bodies": 0,  # Bu ma'lumot kerak bo'lsa, GovernmentBody modelidan ol
        }
    except Exception as e:
        logger.error(f"get_region_stats xatosi: {str(e)}")
        return {}