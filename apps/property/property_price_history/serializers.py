from apps.core.serializers.base_bulk import BaseBulkSerializer
from apps.property.property_price_history.models import PropertyPriceHistory
from rest_framework import serializers


class PropertyPriceHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = PropertyPriceHistory
        fields = [
            'id',
            'property',
            'date_recorded',
            'price',
            'currency',
            'source',
        ]
        list_serializer_class = BaseBulkSerializer

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['property'] = instance.property.name_uz if instance.property else None
        return data