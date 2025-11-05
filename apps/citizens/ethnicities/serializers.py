from rest_framework import serializers

from .models import Ethnicity, EthnicityPopulation
from ...shared.serializers import BaseNameValidationSerializer


class EthnicitySerializer(BaseNameValidationSerializer):
    name_field = ['name_uz', 'name_ru', 'name_uz_cyr']

    class Meta:
        model = Ethnicity
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


class EthnicityPopulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EthnicityPopulation
        fields = [
            'id',
            'population',
            'ethnicity',
            'count'
        ]
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['population'] = instance.population.population_density if instance.population else None
        return data