
from apps.shared.models import BaseTimeModel
from django.db import models

USER, ADMIN = ('user', 'admin')

class User(BaseTimeModel):

    USER_ROLES = (
        (ADMIN, ADMIN),
        (USER, USER),
    )

    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default=USER)
    is_active = models.BooleanField(default=True)


class SearchQuery(BaseTimeModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='searches')
    user_query = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    radius_miles = models.DecimalField(max_digits=5, decimal_places=2)
    filters = models.JSONField(null=True, blank=True)
