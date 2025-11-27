from apps.areas.districts.models import District
from apps.shared.models import BaseTimeModel
from django.db import models

class PeopleEducation(BaseTimeModel):
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    regional_school = models.IntegerField()
    regional_kindergarten = models.IntegerField()
    regional_teachers = models.IntegerField()
    regional_students = models.IntegerField()

    def __str__(self):
        return f"{self.district} has {self.regional_school} schools and {self.regional_kindergarden} kindergartens"
