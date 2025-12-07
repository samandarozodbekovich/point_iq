from apps.networks.models import CellTower
from apps.competitors.competitor.models import Competitor
from apps.citizens.people_consume.models import PeopleConsume
from apps.citizens.people_education.models import PeopleEducation
from apps.government_bodies.models import GovernmentBody


def get_region_stats(region_coords, radius=0.2):
    """
    Hudud statistikasi
    """
    if region_coords:
        lat, lon = region_coords
        towers = CellTower.objects.filter(
            latitude__gte=lat - radius,
            latitude__lte=lat + radius,
            longitude__gte=lon - radius,
            longitude__lte=lon + radius
        )
        nearest = list(towers.values("id", "latitude", "longitude"))
    else:
        nearest = []

    return {
        "nearest_towers": nearest,
        "population": PeopleConsume.objects.count(),
        "education": PeopleEducation.objects.count(),
        "competitors": Competitor.objects.count(),
        "gov_body": GovernmentBody.objects.count(),
    }
