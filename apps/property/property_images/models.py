from django.db import models

from apps.property.property_listing.models import PropertyListing
from apps.shared.models import BaseTimeModel, SoftDeleteManager


class PropertyImage(BaseTimeModel):
    property = models.ForeignKey(PropertyListing, on_delete=models.SET_NULL , null=True, blank=True, related_name='images')
    image = models.ImageField(upload_to='properties/property_images')
    is_deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()  # excludes soft-deleted rows
    all_objects = models.Manager()

    def __str__(self):
        return self.property.owner.phone_number

