import requests
from django.contrib.gis.geos import Point, LineString
from django.db import transaction

from apps.ai.logger import logger
from apps.dictionary.population_traffic.models.point_of_interest import PointOfInterestModel
from apps.dictionary.population_traffic.models.traffic_note import TrafficNoteModel
from apps.dictionary.population_traffic.models.traffic_segment import TrafficSegmentModel

OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

# How strongly each POI category attracts foot traffic.
POI_WEIGHTS = {
    "restaurant": 10.0,
    "fast_food": 12.0,
    "cafe": 7.0,
    "supermarket": 15.0,
    "convenience": 6.0,
    "pharmacy": 8.0,
    "bank": 9.0,
    "bus_station": 11.0,
}
DEFAULT_POI_WEIGHT = 3.0


def area_cache_key(state, lat, lng, radius):
    """Cache key for one fetch area; ~100 m rounding so nearby clicks share it."""
    return f"overpass:{state}:{round(float(lat), 3)}:{round(float(lng), 3)}:{int(radius)}"


def fetch_overpass(lat, lng, radius):
    """Download raw Overpass data.

    Network and server errors are raised, not swallowed, so the caller can
    retry them; they are the failures a retry can actually fix.
    """
    logger.info("Overpass API ga optimallashtirilgan so'rov yuborilmoqda...")
    query = f"""
            [out:json][timeout:60];
            (
              node["amenity"~"bus_station|cafe|restaurant|fast_food|bank"](around:{radius},{lat},{lng});
              node["railway"="station"](around:{radius},{lat},{lng});
              node["shop"~"supermarket|convenience|pharmacy"](around:{radius},{lat},{lng});
              way["highway"~"primary|secondary|tertiary|residential"](around:{radius},{lat},{lng});
            );
            out geom;
            """
    response = requests.get(OVERPASS_URL, params={'data': query}, timeout=60)
    response.raise_for_status()
    return response.json()


@transaction.atomic
def save_elements(data):
    """Store Overpass elements. All or nothing, so a failure can't leave half an area."""
    counts = {'nodes': 0, 'pois': 0, 'ways': 0}

    for el in data.get('elements', []):
        tags = el.get('tags', {})

        # 1. Transport bog'lamalari (TrafficNoteModel)
        if tags.get("amenity") == "bus_station" or tags.get("railway") == "station":
            TrafficNoteModel.objects.update_or_create(
                external_id=f"node/{el['id']}",
                defaults={
                    'name': tags.get('name', f"Station {el['id']}"),
                    'location': Point(el['lon'], el['lat'], srid=4326),
                    "node_type": "transit",
                    'base_weight': 10
                }
            )
            counts['nodes'] += 1

        # 2. POI (PointOfInterestModel). No zone_color: only road segments have one.
        elif el['type'] == 'node':
            category = tags.get('shop') or tags.get('amenity') or tags.get('railway')

            PointOfInterestModel.objects.update_or_create(
                external_id=f"node/{el['id']}",
                defaults={
                    'name': tags.get('name', f"{category or 'Noma`lum'}"),
                    'location': Point(el['lon'], el['lat'], srid=4326),
                    'category': category,
                    'attraction_factor': POI_WEIGHTS.get(category, DEFAULT_POI_WEIGHT),
                    'influence_radius': 500
                }
            )
            counts['pois'] += 1

        # 3. Yo'llar (TrafficSegmentModel)
        elif el['type'] == 'way' and 'highway' in tags:
            geom = el.get('geometry', [])
            if len(geom) > 1:
                h_type = tags.get('highway')
                road_color = "#3498db"
                if h_type in ['primary', 'trunk']:
                    road_color = "#2c3e50"

                TrafficSegmentModel.objects.update_or_create(
                    external_id=f"way/{el['id']}",
                    defaults={
                        'street_name': tags.get('name', "Nomsiz ko'cha"),
                        'line': LineString([(pt['lon'], pt['lat']) for pt in geom], srid=4326),
                        'intensity_level': 'high' if h_type in ['primary', 'trunk'] else 'medium',
                        'zone_color': road_color
                    }
                )
                counts['ways'] += 1

    logger.info(f"Yakunlandi: {counts['nodes']} stansiya, {counts['pois']} POI, {counts['ways']} ko'cha saqlandi.")
    return counts


def get_fetch_data(lat, lng, radius):
    return save_elements(fetch_overpass(lat, lng, radius))
