from django.db import models

from apps.shared.models import BaseTimeModel
from apps.areas.districts.models import District

# Uzbekistan (MCC 434) mobile network codes. Integer keys: OpenCellID and
# the mnc column hold numbers, so the old '01'-style string keys never matched.
OPERATORS_BY_MNC = {
    1: 'Beeline',
    2: 'Ucell',
    4: 'Beeline',  # in some regions
    5: 'Ucell',
    7: 'Mobiuz (UMS)',
    99: 'Uztelecom (Uzmobile)',
}


class LocationScore(models.Model):
    district = models.OneToOneField(District, on_delete=models.SET_NULL , null=True, blank=True)
    location_score = models.FloatField()

    def __str__(self):
        return f"{self.district.name_uz} - {self.location_score}"


class CellTower(BaseTimeModel):
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    radio = models.CharField(max_length=10)
    mcc = models.IntegerField()
    mnc = models.IntegerField()
    lac = models.IntegerField(null=True, blank=True)
    cellid = models.BigIntegerField()
    range_meters = models.IntegerField(null=True, blank=True)
    samples = models.IntegerField(null=True, blank=True)
    changeable = models.BooleanField(default=False)

    class Meta:
        db_table = "cell_towers"

    @property
    def operator_name(self):
        # Derived from the MNC instead of stored: it can never go stale or
        # disagree with mnc.
        return OPERATORS_BY_MNC.get(self.mnc, "Unknown")



