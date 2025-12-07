from django.db import models

from apps.shared.models import BaseTimeModel
from apps.areas.districts.models import District


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



