from apps.areas.districts.models import District
from apps.core.serializers.base_bulk_list import BaseBulkListSerializer
from apps.shared.serializers import BaseNameValidationSerializer


class DistrictSerializer(BaseNameValidationSerializer):
    name_field = ['name_uz', 'name_ru', 'name_cyr']

    class Meta:
        model = District
        fields = [
            'id',
            'name_uz',
            'name_ru',
            'name_cyr',
            'city'
        ]
        list_serializer_class = BaseBulkListSerializer

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['city'] = instance.city.name_uz if instance.city else None
        return data

    def validate(self, data):
        data = BaseNameValidationSerializer.validate(self, data)
        return data