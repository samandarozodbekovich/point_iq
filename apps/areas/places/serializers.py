from apps.areas.places.models import Place
from apps.core.serializers.base_bulk_list import BaseBulkListSerializer
from apps.shared.serializers import BaseNameValidationSerializer


class PlaceSerializer(BaseNameValidationSerializer, BaseBulkListSerializer):
    name_field = ['name_uz', 'name_ru', 'name_uz_cyr']

    class Meta:
        model = Place
        fields = [
            'id',
            'name_uz',
            'name_ru',
            'name_uz_cyr',
            'street',
            'house_number',
            'latitude',
            'longitude',
            'description',
        ]

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