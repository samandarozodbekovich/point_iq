from django.db import models

from apps.property.property_listing.models import PropertyListing


class PropertyPriceHistory(models.Model):
    property = models.ForeignKey(PropertyListing, on_delete=models.CASCADE, related_name='price_history')
    date_recorded = models.DateField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10)
    source = models.CharField(max_length=100)