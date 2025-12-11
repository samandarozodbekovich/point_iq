
import json
from django.core.management.base import BaseCommand
from apps.areas.districts.models import District
from apps.areas.cities.models import City


class Command(BaseCommand):
    help = 'upload district boundaries from GeoJSON files'

    def add_arguments(self, parser):
        parser.add_argument('geojson_file', type=str, help='Path to GeoJSON file')
        parser.add_argument('--city', type=str, help='City name (optional)', default='Tashkent')

    def handle(self, *args, **options):
        file_path = options['geojson_file']
        city_name = options.get('city')

        self.stdout.write(f'Fayl o\'qilmoqda: {file_path}')

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Fayl topilmadi: {file_path}'))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'JSON formatida xatolik: {e}'))
            return

        # City ni topish yoki yaratish
        city = None
        if city_name:
            city, created = City.objects.get_or_create(
                name_uz=city_name,
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