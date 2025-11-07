from django.db import models
from apps.shared.models import BaseTimeModel


class PropertyListing(BaseTimeModel):
    property_type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    description = models.TextField()
    address = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10)
    area_sq_m = models.DecimalField(max_digits=10, decimal_places=2)
    rooms = models.IntegerField()
    floor = models.IntegerField()
    total_floors = models.IntegerField()
    year_built = models.IntegerField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    listing_url = models.TextField()
    source = models.CharField(max_length=100)
    is_for_sale = models.BooleanField(default=False)
    is_for_rent = models.BooleanField(default=False)
