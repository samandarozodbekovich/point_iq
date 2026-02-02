from apps.areas.districts.models import District
from apps.shared.models import BaseTimeModel
from django.db import models

class PeopleEducation(BaseTimeModel):
    district = models.ForeignKey(District, on_delete=models.SET_NULL , null=True, blank=True)
    regional_school = models.IntegerField(null=True, blank=True)
    regional_kindergarten = models.IntegerField(null=True, blank=True)
    regional_teachers = models.IntegerField(null=True, blank=True)
    regional_students = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.district} has {self.regional_school} schools and {self.regional_kindergarten} kindergartens"