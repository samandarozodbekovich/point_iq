from apps.ai.logger import logger
from apps.networks.models import CellTower

from apps.citizens.people_consume.models import PeopleConsume
from apps.citizens.people_education.models import PeopleEducation



def get_region_stats(region_coord=None, radius=0.2):
    try:
        if not region_coord:
            return {}

        lat, lon = region_coord

        towers = CellTower.objects.filter(
            latitude__gte=lat - radius,
            latitude__lte=lat + radius,
            longitude__gte=lon - radius,
            longitude__lte=lon + radius
        )

        nearest = list(towers.values("id", "latitude", "longitude", "operator_name"))

        return {
            "coordinates": region_coord,
            "nearest_towers": nearest,
            "towers_count": len(nearest),
            "population": PeopleConsume.objects.count(),
            "education_centers": PeopleEducation.objects.count(),
            "competitors": 0,
            "gov_bodies": 0,
        }
    except Exception as e:
        logger.error(f"get_region_stats error: {str(e)}")
        return {}