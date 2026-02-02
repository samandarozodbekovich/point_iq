from apps.areas.districts.models import District
from apps.shared.models import BaseTimeModel
from django.db import models

class PeopleConsume(BaseTimeModel):
    district = models.ForeignKey(District, on_delete=models.SET_NULL , null=True, blank=True)
    month = models.CharField(max_length=10, null=True, blank=True)
    year = models.CharField(max_length=4, null=True, blank=True)
    consume_gas = models.IntegerField(null=True, blank=True)
    consume_electric = models.IntegerField(null=True, blank=True)
    bus_station = models.IntegerField(null=True, blank=True)

    def __str__(self):
<<<<<<< HEAD
        return f'people of {self.district__name_uz} in {self.month} of {self.year}'
=======
        return f'people of {self.district} in {self.month} of {self.year}'
>>>>>>> 7cb6155 (Initial clean commit)
