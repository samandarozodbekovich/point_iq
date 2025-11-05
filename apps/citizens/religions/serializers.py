from rest_framework import serializers

from .models import Religion, ReligionCount
from ...shared.serializers import BaseNameValidationSerializer


class ReligionSerializer(BaseNameValidationSerializer):
    name_field = ['name_uz', 'name_ru', 'name_cyr']

    class Meta:
        model = Religion
        fields = [
            'id',
            'name_uz',
            'name_ru',
            'name_cyr',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def validate(self, data):
        data = BaseNameValidationSerializer.validate(self, data)
        return data

class ReligionCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReligionCount
        fields = ['id', 'population','religion', 'count']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['population'] = instance.population.population_density if instance.population else None
        data['religion'] = instance.religion.name if instance.religion else None
        return data

