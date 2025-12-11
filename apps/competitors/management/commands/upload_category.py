import json

from apps.competitors.competitor_categories.models import CompetitorCategory
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('category_json_file', type=str, help='json file with competitor categories')

    def handle(self, *args, **options):
        file_path = options['category_json_file']
        self.stdout.write(f"reading file {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(f'file {file_path} not fount')
        except json.JSONDecodeError as e:
            self.stdout.write(f"error json file format {e}")

        loaded_count = 0

        for i in data:
            competitor_category, created = CompetitorCategory.objects.update_or_create(
                external_id=i['external_id'],
                defaults={
                    'name_uz':i['name_uz'],
                    'name_ru':i['name_ru'],
                    'name_cyr':i['name_cyr'],
                }
            )

            action = "Created" if created else "Updated"
            loaded_count += 1
        self.stdout.write(f'uploaded {loaded_count} competitor categories')