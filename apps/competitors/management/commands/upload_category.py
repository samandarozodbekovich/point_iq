import json

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.competitors.competitor_categories.models import CompetitorCategory


class Command(BaseCommand):
    help = (
        "Load competitor categories from JSON (name_uz, name_ru, name_cyr, google_type). "
        "Run with --dry-run first on an existing database."
    )

    def add_arguments(self, parser):
        parser.add_argument('category_json_file', type=str, help='json file with competitor categories')
        parser.add_argument('--dry-run', action='store_true',
                            help='show what would be created/updated without writing')

    def handle(self, *args, **options):
        file_path = options['category_json_file']
        dry_run = options['dry_run']
        self.stdout.write(f"reading file {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise CommandError(f'file {file_path} not found')
        except json.JSONDecodeError as e:
            raise CommandError(f"error json file format {e}")

        created_count = updated_count = 0

        # All or nothing: a bad row halfway must not leave half a load behind.
        with transaction.atomic():
            for item in data:
                category = self.find_existing(item)
                fields = {
                    'name_uz': item['name_uz'],
                    'name_ru': item['name_ru'],
                    'name_cyr': item['name_cyr'],
                }
                # Don't wipe a google_type set in the admin when the file has none.
                if item.get('google_type'):
                    fields['google_type'] = item['google_type']

                if category is None:
                    created_count += 1
                    self.stdout.write(f"  create: {item['name_uz']}")
                    if not dry_run:
                        CompetitorCategory.objects.create(**fields)
                else:
                    updated_count += 1
                    self.stdout.write(f"  update: #{category.pk} {category.name_uz}")
                    if not dry_run:
                        for name, value in fields.items():
                            setattr(category, name, value)
                        category.save()

            if dry_run:
                transaction.set_rollback(True)

        prefix = "[dry run] would be: " if dry_run else ""
        self.stdout.write(self.style.SUCCESS(
            f'{prefix}competitor categories: {created_count} created, {updated_count} updated'
        ))

    @staticmethod
    def find_existing(item):
        """Match on name_uz, then name_ru, ignoring case.

        external_id was dropped in migration 0004, so names are the only key.
        Trying both and ignoring case keeps a small spelling or case
        difference on the server from silently creating a duplicate.
        """
        for field in ('name_uz', 'name_ru'):
            category = CompetitorCategory.objects.filter(**{f'{field}__iexact': item[field]}).first()
            if category is not None:
                return category
        return None
