from rest_framework import serializers

from .models import PopulationStatistic
from ...core.serializers.base_bulk_list import BaseBulkListSerializer
from ...shared.serializers import BaseNameValidationSerializer


class PopulationStatisticSerializer(serializers.ModelSerializer):

    class Meta:
        model = PopulationStatistic
        fields = [
            'id',
            'population',
            'age_group',
            'population_count',
        ]
        list_serializer_class = BaseBulkListSerializer


    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def validate(self, data):
        data = BaseNameValidationSerializer.validate(self, data)
        return data