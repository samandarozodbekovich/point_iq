import json
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from django.core.management.base import BaseCommand
from apps.areas.districts.models import District
from apps.areas.cities.models import City


class Command(BaseCommand):
    help = 'Upload district boundaries from GeoJSON files'

    def add_arguments(self, parser):
        parser.add_argument('geojson_file', type=str, help='Path to GeoJSON file')
        parser.add_argument('--city', type=str, help='City name (optional)', default='Tashkent')

    def handle(self, *args, **options):
        file_path = options['geojson_file']
        city_name = options.get('city')

        self.stdout.write(f'reading file: {file_path}')

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'not found: {file_path}'))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'JSON form error: {e}'))
            return

        # find or create city
        city = None
        if city_name:
            city, created = City.objects.get_or_create(
                name_uz=city_name,
                defaults={
                    'name_ru': city_name,
                    'name_cyr': city_name
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'created city: {city_name}'))

        loaded_count = 0

        for feature in data.get('features', []):
            geometry = feature.get('geometry')
            if not geometry:
                continue

            gtype = geometry.get('type')

            # --- Polygon / MultiPolygon support ---
            if gtype == 'Polygon':
                coordinates = geometry.get('coordinates', [])
                if not coordinates:
                    continue
                coord = coordinates[0]

            elif gtype == 'MultiPolygon':
                coordinates = geometry.get('coordinates', [])
                if not coordinates or not coordinates[0]:
                    continue
                coord = coordinates[0][0]

            else:
                continue

            # The full geometry, every part of a MultiPolygon included.
            # boundary_json above keeps only the first ring, which dropped
            # the second part of Mirzo Ulug'bek.
            boundary = GEOSGeometry(json.dumps(geometry), srid=4326)
            if boundary.geom_type == 'Polygon':
                boundary = MultiPolygon(boundary, srid=4326)
            if not boundary.valid:
                boundary = boundary.buffer(0)  # repair self-intersections
                if boundary.geom_type == 'Polygon':
                    boundary = MultiPolygon(boundary, srid=4326)

            # --- Properties ---
            props = feature.get('properties', {})

            name_uz = props.get('name', '').strip()
            name_cyr = props.get('name:cyr', '').strip()
            name_ru = props.get('name:ru', '').strip()

            # fallback: wikipedia
            if not name_uz:
                wiki = props.get('wikipedia', '')
                if wiki.startswith('ru:'):
                    name_ru = wiki.replace('ru:', '').strip()
                    name_uz = name_ru
                    name_cyr = name_ru

            # still no name → skip
            if not name_uz:
                self.stdout.write(self.style.WARNING('district name not found, skipped'))
                continue

            district, created = District.objects.update_or_create(
                name_uz=name_uz,
                city=city,
                defaults={
                    'name_ru': name_ru or name_uz,
                    'name_cyr': name_cyr or name_uz,
                    'boundary_json': coord,
                    'boundary': boundary,
                }
            )

            action = 'created' if created else 'updated'
            self.stdout.write(f'{action}: {district.name_uz} ({len(coord)} nuqta)')
            loaded_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Jami {loaded_count} ta tuman yuklandi!')
        )