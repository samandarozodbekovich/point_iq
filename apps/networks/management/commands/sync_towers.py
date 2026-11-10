import requests
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.networks.models import CellTower

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Load mobile cell towers in Tashkent from OpenCellID"

    # API and area settings
    OPENCELLID_KEY = settings.OPENCELLID_KEY  # from .env; no fallback key in code
    TASHKENT_BBOX = "41.2,69.1,41.4,69.3"  # minLat,minLon,maxLat,maxLon

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Updating cell towers..."))

        url = "https://opencellid.org/cell/getInArea"
        params = {
            'key': self.OPENCELLID_KEY,
            'bbox': self.TASHKENT_BBOX,
            'format': 'json',
            'limit': 500
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"API error: {response.status_code}"))
                return

            cells = response.json()
            if not isinstance(cells, list):
                self.stdout.write(self.style.ERROR("Unexpected API response format."))
                return

            created_count = 0
            updated_count = 0

            for cell in cells:
                # Match existing rows by the cell's unique identifier:
                # radio, mcc, mnc, lac and cellid together
                tower, created = CellTower.objects.update_or_create(
                    radio=cell.get('radio'),
                    mcc=cell.get('mcc'),
                    mnc=cell.get('mnc'),
                    lac=cell.get('lac') or cell.get('tac'),
                    cellid=cell.get('cellid') or cell.get('cid'),
                    # The operator is derived from mnc (CellTower.operator_name),
                    # there is no column for it.
                    defaults={
                        'latitude': cell.get('lat'),
                        'longitude': cell.get('lon'),
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            self.stdout.write(self.style.SUCCESS(
                f"Done. Created: {created_count}, updated: {updated_count}"
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
