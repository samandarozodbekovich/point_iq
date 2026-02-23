import requests
from django.contrib.gis.geos import Point, LineString

from apps.ai.logger import logger
from apps.dictionary.population_traffic.models.point_of_interest import PointOfInterestModel
from apps.dictionary.population_traffic.models.traffic_note import TrafficNoteModel
from apps.dictionary.population_traffic.models.traffic_segment import TrafficSegmentModel


def get_fetch_data(lat, lng, radius):
    logger.info("Overpass API ga optimallashtirilgan so'rov yuborilmoqda...")

    # Overpass serverlari
    overpass_url = "https://overpass.kumi.systems/api/interpreter"

    query = f"""
            [out:json][timeout:60];
            (
              node["amenity"~"bus_station|cafe|restaurant|fast_food|bank"](around:{radius},{lat},{lng});
              node["shop"~"supermarket|convenience|pharmacy"](around:{radius},{lat},{lng});
              way["highway"~"primary|secondary|tertiary|residential"](around:{radius},{lat},{lng});
            );
            out geom;
            """
    try:
        response = requests.get(overpass_url, params={'data': query}, timeout=60)
        if response.status_code != 200:
            logger.error(f"API Error: {response.status_code}")
            return
        data = response.json()
    except Exception as e:
        logger.error(f"Xatolik yuz berdi: {e}")
        return

    # Kategoriya konfiguratsiyasi
    CATEGORY_MAP = {
        "restaurant": {"color": "#FF4500", "weight": 10.0},
        "fast_food": {"color": "#FF0000", "weight": 12.0},
        "cafe": {"color": "#FF6347", "weight": 7.0},
        "supermarket": {"color": "#FFD700", "weight": 15.0},
        "convenience": {"color": "#FFA500", "weight": 6.0},
        "pharmacy": {"color": "#00FF7F", "weight": 8.0},
        "bank": {"color": "#1E90FF", "weight": 9.0},
        "bus_station": {"color": "#0000FF", "weight": 11.0},
    }

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

        # 2. POI (PointOfInterestModel)
        elif el['type'] == 'node':
            category = tags.get('shop') or tags.get('amenity') or tags.get('railway')
            config = CATEGORY_MAP.get(category, {"color": "gray", "weight": 3.0})

            PointOfInterestModel.objects.update_or_create(
                external_id=f"node/{el['id']}",
                defaults={
                    'name': tags.get('name', f"{category or 'Noma`lum'}"),
                    'location': Point(el['lon'], el['lat'], srid=4326),
                    'category': category,
                    'attraction_factor': config['weight'],
                    'zone_color': config['color'],
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