
from apps.property.property_listing.models import PropertyListing
from rest_framework import serializers


class PropertyListingSerializer(serializers.ModelSerializer):

    class Meta:
        model = PropertyListing
        fields = [
            'property_type',
            'title',
            'description',
            'address',
            'price',
            'currency',
            'area_sq_m',
            'rooms',
            'floor',
            'total_floors',
            'year_built',
            'latitude',
            'longitude',
            'listing_url',
            'is_for_sale',
            'is_for_rent',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data
