from apps.core.serializers.base_bulk import BaseBulkSerializer
from apps.property.property_listing.models import PropertyListing
from rest_framework import serializers


class PropertyListingSerializer(serializers.ModelSerializer):

    class Meta:
        model = PropertyListing
        fields = '__all__'

        list_serializer_class = BaseBulkSerializer

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['area'] = instance.area.name_uz if instance.area else None
        data['street'] = instance.street.name_uz if instance.street else None
        data['place'] = instance.place.house_number if instance.place else None
        return data
