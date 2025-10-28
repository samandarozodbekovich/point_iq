from .models import Religion
from ...core.serializers.base_bulk_list import BaseBulkListSerializer
from ...shared.serializers import BaseNameValidationSerializer


class ReligionSerializer(BaseNameValidationSerializer):
    name_field = ['name_uz', 'name_ru', 'name_uz_cyr']

    class Meta:
        model = Religion
        fields = [
            'id',
            'name_uz',
            'name_ru',
            'name_uz_cyr',
        ]
        list_serializer_class = BaseBulkListSerializer


    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def validate(self, data):
        data = BaseNameValidationSerializer.validate(self, data)
        return data