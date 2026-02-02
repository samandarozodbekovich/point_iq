<<<<<<< HEAD

=======
>>>>>>> 7cb6155 (Initial clean commit)
import json
from django.core.management.base import BaseCommand
from apps.areas.districts.models import District
from apps.areas.cities.models import City


class Command(BaseCommand):
<<<<<<< HEAD
    help = 'upload district boundaries from GeoJSON files'
=======
    help = 'Upload district boundaries from GeoJSON files'
>>>>>>> 7cb6155 (Initial clean commit)

    def add_arguments(self, parser):
        parser.add_argument('geojson_file', type=str, help='Path to GeoJSON file')
        parser.add_argument('--city', type=str, help='City name (optional)', default='Tashkent')

    def handle(self, *args, **options):
        file_path = options['geojson_file']
        city_name = options.get('city')

<<<<<<< HEAD
        self.stdout.write(f'Fayl o\'qilmoqda: {file_path}')
=======
        self.stdout.write(f'reading file: {file_path}')
>>>>>>> 7cb6155 (Initial clean commit)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
<<<<<<< HEAD
            self.stdout.write(self.style.ERROR(f'Fayl topilmadi: {file_path}'))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'JSON formatida xatolik: {e}'))
            return

        # City ni topish yoki yaratish
=======
            self.stdout.write(self.style.ERROR(f'not found: {file_path}'))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'JSON form error: {e}'))
            return

        # find or create city
>>>>>>> 7cb6155 (Initial clean commit)
        city = None
        if city_name:
            city, created = City.objects.get_or_create(
                name_uz=city_name,
<<<<<<< HEAD
                defaults={'name_ru': city_name, 'name_cyr': city_name}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Shahar yaratildi: {city_name}'))

        loaded_count = 0
        for feature in data.get('features', []):
            geometry = feature.get('geometry', {})

            if geometry.get('type') == 'Polygon':
                # Polygon koordinatalarini olish
                coords = geometry.get('coordinates', [[]])[0]

                props = feature.get('properties', {})
                name_uz = props.get('name', '')
                name_en = props.get('name:en', '')
                name_ru = props.get('name:ru', '')

                if not name_uz:
                    self.stdout.write(self.style.WARNING('Name topilmadi, o\'tkazib yuborildi'))
                    continue

                # District yaratish yoki yangilash
                district, created = District.objects.update_or_create(
                    name_uz=name_uz,
                    defaults={
                        'name_ru': name_ru or name_uz,
                        'name_cyr': name_ru or name_uz,
                        'boundary_json': coords,  # JSON sifatida saqlash
                        'city': city
                    }
                )

                action = "Yaratildi" if created else "Yangilandi"
                self.stdout.write(f'{action}: {district.name_uz} ({len(coords)} nuqta)')
                loaded_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Jami {loaded_count} ta tuman yuklandi!')
        )
=======
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
                }
            )

            action = 'created' if created else 'updated'
            self.stdout.write(f'{action}: {district.name_uz} ({len(coord)} nuqta)')
            loaded_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Jami {loaded_count} ta tuman yuklandi!')
        )
>>>>>>> 7cb6155 (Initial clean commit)
