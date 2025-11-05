from apps.core.serializers.base_bulk import BaseBulkSerializer
from apps.property.property_images.models import PropertyImage
from rest_framework import serializers


class PropertyImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = PropertyImage
        fields = [
            'id',
            'property',
            'image',
        ]
        list_serializer_class = BaseBulkSerializer

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['property'] = instance.property.name_uz if instance.property else None
        return data
