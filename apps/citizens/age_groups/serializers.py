from rest_framework import serializers

from .models import AgeGroup, AgeGroupPopulation
from ...core.serializers.base_bulk_list import BaseBulkListSerializer
from ...shared.serializers import BaseNameValidationSerializer


class AgeGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = AgeGroup
        fields = [
            'id',
            'age_group',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data


class AgeGroupPopulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgeGroupPopulation
        fields = [
            'id',
            'population',
            'age_group',
            'count',
        ]
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data
