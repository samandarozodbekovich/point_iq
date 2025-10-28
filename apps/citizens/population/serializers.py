from rest_framework import serializers

from .models import Population
from ...core.serializers.base_bulk_list import BaseBulkListSerializer
from ...shared.serializers import BaseNameValidationSerializer


class PopulationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Population
        fields = [
            'id',
            'apartment',
            'count_male',
            'count_female',
            'average_income',
            'unemployment_rate',
            'population_density',
        ]
        list_serializer_class = BaseBulkListSerializer


    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def validate(self, data):
        data = BaseNameValidationSerializer.validate(self, data)
        return data