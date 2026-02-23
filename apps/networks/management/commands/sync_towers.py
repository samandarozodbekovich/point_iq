import requests
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.networks.models import CellTower

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "OpenCellID orqali Toshkent hududidagi mobil minoralarni bazaga yuklash"

    # API va Koordinata sozlamalari
    OPENCELLID_KEY = getattr(settings, 'OPENCELLID_KEY', '***REMOVED***')
    TASHKENT_BBOX = "41.2,69.1,41.4,69.3"  # minLat,minLon,maxLat,maxLon

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Minoralar bazasini yangilash boshlandi..."))

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
                self.stdout.write(self.style.ERROR(f"API Xatosi: {response.status_code}"))
                return

            cells = response.json()
            if not isinstance(cells, list):
                self.stdout.write(self.style.ERROR("API noto'g'ri formatda javob qaytardi."))
                return

            created_count = 0
            updated_count = 0

            for cell in cells:
                # Bazada bor yoki yo'qligini tekshirish (Unique identifier orqali)
                # Odatda radio, mcc, mnc, lac va cellid kombinatsiyasi unikal bo'ladi
                tower, created = CellTower.objects.update_or_create(
                    radio=cell.get('radio'),
                    mcc=cell.get('mcc'),
                    mnc=cell.get('mnc'),
                    lac=cell.get('lac') or cell.get('tac'),
                    cellid=cell.get('cellid') or cell.get('cid'),
                    defaults={
                        'latitude': cell.get('lat'),
                        'longitude': cell.get('lon'),
                        'operator_name': self.guess_operator(cell.get('mnc')),
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            self.stdout.write(self.style.SUCCESS(
                f"Tugatildi! Yangi: {created_count}, Yangilandi: {updated_count}"
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Xatolik yuz berdi: {str(e)}"))

    def guess_operator(self, mnc):
        """MNC kodiga qarab operator nomini taxmin qilish (O'zbekiston uchun)"""
        operators = {
            '01': 'Beeline',
            '02': 'Ucell',
            '04': 'Beeline',  # Ba'zi hududlarda
            '05': 'Ucell',
            '07': 'Mobiuz (UMS)',
            '99': 'Uztelecom (Uzmobile)'
        }
        return operators.get(str(mnc), "Noma'lum")