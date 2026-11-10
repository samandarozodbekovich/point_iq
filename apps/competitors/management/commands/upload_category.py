import json

from apps.competitors.competitor_categories.models import CompetitorCategory
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Load competitor categories from JSON (name_uz, name_ru, name_cyr, google_type)"

    def add_arguments(self, parser):
        parser.add_argument('category_json_file', type=str, help='json file with competitor categories')

    def handle(self, *args, **options):
        file_path = options['category_json_file']
        self.stdout.write(f"reading file {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise CommandError(f'file {file_path} not found')
        except json.JSONDecodeError as e:
            raise CommandError(f"error json file format {e}")

        created_count = updated_count = 0

        for item in data:
            defaults = {
                'name_ru': item['name_ru'],
                'name_cyr': item['name_cyr'],
            }
            # Don't wipe a google_type set in the admin when the file has none.
            if item.get('google_type'):
                defaults['google_type'] = item['google_type']

            # external_id was dropped in migration 0004; name_uz is the
            # remaining natural key and is unique within the file.
            _, created = CompetitorCategory.objects.update_or_create(
                name_uz=item['name_uz'],
                defaults=defaults,
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'competitor categories: {created_count} created, {updated_count} updated'
        ))
