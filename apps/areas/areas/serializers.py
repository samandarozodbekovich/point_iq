from apps.shared.serializers import BaseNameValidationSerializer
from .models import Area
from ...core.serializers.base_bulk_list import BaseBulkListSerializer


class AreaSerializer(BaseNameValidationSerializer, BaseBulkListSerializer):
    name_field = ['name_uz', 'name_ru', 'name_uz_cyr']

    class Meta:
        model = Area
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['city'] = instance.city.name_uz if instance.city else None
        data['district'] = instance.district.name_uz if instance.district else None
        return data

    def validate(self, data):
        data = BaseNameValidationSerializer.validate(self, data)
        return data
