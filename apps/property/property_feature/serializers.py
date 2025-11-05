from apps.core.serializers.base_bulk import BaseBulkSerializer
from apps.property.property_feature.models import PropertyFeature
from apps.shared.serializers import BaseNameValidationSerializer


class PropertyFeatureSerializer(BaseNameValidationSerializer):
    name_field = ['name_uz', 'name_ru', 'name_cyr']

    class Meta:
        model = PropertyFeature
        fields = [
            'id',
            'name_uz',
            'name_ru',
            'name_uz_cyr',
            'property',
            'feature_value',
        ]
        list_serializer_class = BaseBulkSerializer


    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['property'] = instance.property.name_uz if instance.property else None
        return data

    def validate(self, data):
        data = BaseNameValidationSerializer.validate(self, data)
        return data