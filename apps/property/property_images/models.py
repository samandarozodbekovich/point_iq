from django.db import models

from apps.property.property_listing.models import PropertyListing
from apps.shared.models import BaseTimeModel


class PropertyImage(BaseTimeModel):
    property = models.ForeignKey(PropertyListing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/property_images')

