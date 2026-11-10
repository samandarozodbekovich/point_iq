import requests
from django.core.management.base import BaseCommand, CommandError

from apps.dictionary.utils.fetch_tashkent_data import fetch_overpass, save_elements


class Command(BaseCommand):
    help = 'fetch tashkent data'

    def add_arguments(self, parser):
        parser.add_argument('--lat', type=float, default=41.311081)
        parser.add_argument('--lng', type=float, default=69.240562)
        parser.add_argument('--radius', type=int, default=800)

    def handle(self, *args, **options):
        # Reuses the same fetch/save code as the Celery task. The command
        # used to carry its own copy, which queried the API twice and
        # compared string literals ("amenity" == "bus_station"), so it never
        # saved a single station.
        self.stdout.write("Querying the Overpass API...")
        try:
            data = fetch_overpass(options['lat'], options['lng'], options['radius'])
        except (requests.RequestException, ValueError) as e:
            raise CommandError(f"Overpass error: {e}")

        counts = save_elements(data)
        self.stdout.write(self.style.SUCCESS(
            f"Completed! {counts['nodes']} station, {counts['pois']} POI and {counts['ways']} streets"
        ))
