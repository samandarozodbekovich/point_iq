from rest_framework import serializers

from .models import EthnicityCount
from ...core.serializers.base_bulk_list import BaseBulkListSerializer
from ...shared.serializers import BaseNameValidationSerializer


class EthnicityCountSerializer(serializers.ModelSerializer):

    class Meta:
        model = EthnicityCount
        fields = [
            'id',
            'population',
            'ethnicity',
            'count'
        ]
        list_serializer_class = BaseBulkListSerializer


    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def validate(self, data):
        data = BaseNameValidationSerializer.validate(self, data)
        return data