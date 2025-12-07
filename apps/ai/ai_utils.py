import numpy as np
import faiss
from apps.networks.models import CellTower
from apps.competitors.competitor.models import Competitor
from apps.citizens.people_consume.models import PeopleConsume
from apps.citizens.people_education.models import PeopleEducation
from apps.government_bodies.models import GovernmentBody

index = None
tower_ids = None
people_consume_data = None
people_education_data = None

def build_vector_db(region_coords=None, radius_km=20):

    global index, tower_ids, people_consume_data, people_education_data

    towers = CellTower.objects.all()
    if region_coords:
        lat, lon = region_coords
        # radius kattalashtirildi
        towers = towers.filter(
            latitude__gte=lat-0.2, latitude__lte=lat+0.2,
            longitude__gte=lon-0.2, longitude__lte=lon+0.2
        )

    if not towers.exists():
        index, tower_ids = None, None
    else:
        vectors = []
        tower_ids = []
        for t in towers:
            vectors.append([float(t.latitude), float(t.longitude)])
            tower_ids.append(t.id)

        vectors = np.array(vectors).astype('float32')
        dim = vectors.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(vectors)

    people_consume_data = list(PeopleConsume.objects.all().values())
    people_education_data = list(PeopleEducation.objects.all().values())

    return index, tower_ids, people_consume_data, people_education_data

def query_ai(user_query: str, region_coords=None, top_k=5):

    global index, tower_ids, people_consume_data, people_education_data

    nearest_towers_info = []
    if index is not None and tower_ids and region_coords:
        vector = np.array([region_coords]).astype('float32')
        D, I = index.search(vector, top_k)
        nearest_ids = [tower_ids[i] for i in I[0]]
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
