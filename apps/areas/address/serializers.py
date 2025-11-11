from apps.areas.address.models import Address
from apps.core.serializers.base_bulk_list import BaseBulkListSerializer
from apps.shared.serializers import BaseNameValidationSerializer


class AddressSerializer(BaseNameValidationSerializer):
    name_field = ['name_uz', 'name_ru', 'name_uz_cyr']

    class Meta:
        model = Address
        fields = [
            'id',
            'name_uz',
            'name_ru',
            'name_uz_cyr',
            'district'
        ]
        list_serializer_class = BaseBulkListSerializer

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['district'] = instance.district.name_uz if instance.district else None
        return data

    def validate(self, data):
        data = super().validate(data)
        return data

