from apps.areas.cities.models import City
from apps.shared.serializers import BaseNameValidationSerializer


class CitySerializer(BaseNameValidationSerializer):
    name_field = ['name_uz', 'name_ru', 'name_uz_cyr']

    class Meta:
        model = City
        fields = [
            'id',
            'name_uz',
            'name_ru',
            'name_uz_cyr',

        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def validate(self, data):
        data = BaseNameValidationSerializer.validate(self, data)
        return data