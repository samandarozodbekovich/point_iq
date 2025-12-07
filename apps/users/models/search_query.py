from apps.shared.models import BaseTimeModel
from django.db import models

from apps.users.models.user import User


class SearchQuery(BaseTimeModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL , null=True, blank=True, related_name='searches')
    user_query = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    radius_miles = models.DecimalField(max_digits=5, decimal_places=2)
    filters = models.JSONField(null=True, blank=True)