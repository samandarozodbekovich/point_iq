from django.db import models

from apps.property.property_listing.models import PropertyListing
from apps.shared.models import BaseNameModel, BaseTimeModel


class PropertyFeature(BaseNameModel, BaseTimeModel):
    property = models.ForeignKey(PropertyListing, on_delete=models.CASCADE, related_name='features')
    feature_value = models.CharField(max_length=255)