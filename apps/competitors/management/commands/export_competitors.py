from itertools import count

from datetime import datetime

from django.core import serializers

from django.core.management.base import BaseCommand
from apps.competitors.competitor.models import Competitor

class Command(BaseCommand):
    help = 'Export competitor data'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help="Output file")
        parser.add_argument('--category', type=str, help='filter by competitor category')
        parser.add_argument('--fields', type=str, help='Comma-separated list of competitor fields')

    def handle(self, *args, **options):
        file = options.get('file')
        category = options.get('category')
        category = category.capitalize() if category else None
        fields = options.get('fields')

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"items_export_competitors_{category}_{fields}.json"

        #filtration
        queryset = Competitor.objects.all()
        if category:
            queryset = queryset.filter(category__name_uz=category)

            # FIELDS
        if fields:
            fields = fields.split(",")
        else:
            fields = None

        total =queryset.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No competitors found'))
            return

        data = serializers.serialize("json", queryset, fields=fields)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(data)

        self.stdout.write(self.style.SUCCESS("Export completed successfully"))


