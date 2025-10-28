from apps.areas.streets.models import Street
from apps.core.serializers.base_bulk_list import BaseBulkListSerializer
from apps.shared.serializers import BaseNameValidationSerializer


class StreetSerializer(BaseNameValidationSerializer):
    name_field = ['name_uz', 'name_ru', 'name_uz_cyr']

    class Meta:
        model = Street
        fields = [
            'id',
            'name_uz',
            'name_ru',
            'name_uz_cyr',
            'area'
        ]
        list_serializer_class = BaseBulkListSerializer

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['area'] = instance.area.name_uz if instance.area else None
        return data

    def validate(self, data):
        data = super().validate(data)
        return data

