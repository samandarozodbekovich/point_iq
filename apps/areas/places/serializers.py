from rest_framework import serializers

from apps.areas.places.models import Place
from apps.core.serializers.base_bulk_list import BaseBulkListSerializer



class PlaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Place
        fields = [
            'id',
            'street',
            'house_number',
            'latitude',
            'longitude',
            'description',
        ]
        list_serializer_class = BaseBulkListSerializer

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['street'] = instance.street.name_uz if instance.street else None
        data['district'] = (
            instance.street.area.district.name_uz if instance.street and instance.street.area else None
        )
        data['city'] = (
            instance.street.area.city.name_uz if instance.street and instance.street.area else None
        )
        data['full_address'] = instance.full_address
        return data

    def validate(self, data):
        data = super().validate(data)
        return data