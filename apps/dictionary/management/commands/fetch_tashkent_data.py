import requests
from django.contrib.gis.geos import Point, LineString
from django.core.management.base import BaseCommand

from ...population_traffic.models.point_of_interest import PointOfInterestModel
from ...population_traffic.models.traffic_note import TrafficNoteModel
from ...population_traffic.models.traffic_segment import TrafficSegmentModel


class Command(BaseCommand):
    help = 'fetch tashkent data'

    def handle(self, *args, **options):
        lat, lng = 41.311081, 69.240562
        radius = 800  # Radiusni boshlanishiga biroz kichraytirdik (1.5 km)

        self.stdout.write("Overpass API ga so'rov yuborilmoqda...")

        overpass_url = "https://overpass-api.de/api/interpreter"

        query = f"""
                [out:json][timeout:90];
                (
                  node["amenity"~"bus_station|cafe|restaurant|fast_food"](around:{radius},{lat},{lng});
                  node["railway"="station"](around:{radius},{lat},{lng});
                  node["shop"~"supermarket|convenience"](around:{radius},{lat},{lng});
                );
                out body;
                """

        try:
            response = requests.get(overpass_url, params={'data': query}, timeout=60)

            # Agar xato qaytsa, javobni ko'rish uchun:
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"API Xatosi: {response.status_code}"))
                self.stdout.write(response.text)
                return

            data = response.json()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Xatolik yuz berdi: {e}"))
            return

        response = requests.get(overpass_url, params={'data': query})
        data = response.json()

        nodes_count=0
        pois_count=0
        ways_count=0

        coords_map = {el['id']:(el['lon'], el['lat']) for el in data['elements']}

        for el in data['elements']:
            tags = el.get('tags', {})

            if el['type'] == "node" and ("amenity" == "bus_station" or 'railway' == 'station'):
                TrafficNoteModel.objects.update_or_create(
                    name = tags.get('name', f"Station {el['id']}"),
                    location = Point(el['lon'], el['lat'], srid=4326),
                    defaults = {'node_type':"transit", "base_weight":8}
                )
                nodes_count += 1

            elif el['type'] == 'node' and ('shop' in tags or 'amenity' in ['cafe', 'fast_food']):
                PointOfInterestModel.objects.get_or_create(
                    name=tags.get('name', f"POI {el['id']}"),
                    location=Point(el['lon'], el['lat'], srid=4326),
                    defaults={
                        'category': tags.get('shop') or tags.get('amenity'),
                        'attraction_factor': 5.0,
                        'influence_radius': 500
                    }
                )
                pois_count += 1

            elif el['type'] == 'way' and 'highway' in tags:
                nodes_in_way = el.get('nodes', [])
                line_coords = [coords_map[node_id] for node_id in nodes_in_way if node_id in coords_map]

                if len(line_coords) > 1:
                    TrafficSegmentModel.objects.get_or_create(
                        street_name=tags.get('name', f"Street {el['id']}"),
                        line=LineString(line_coords, srid=4326),
                        defaults={
                            'intensity_level': 'medium',
                            'zone_color': 'blue'
                        }
                    )
                    ways_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Completed! {nodes_count} station, {pois_count} POI and {ways_count} streets"
        ))


