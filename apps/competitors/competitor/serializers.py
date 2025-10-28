from apps.shared.serializers import BaseNameValidationSerializer
from .models import Competitor
from ...core.serializers.base_bulk_list import BaseBulkListSerializer


class CompetitorSerializer(BaseNameValidationSerializer):
    name_field = ['name_uz', 'name_ru', 'name_uz_cyr']

    class Meta:
        model = Competitor
        fields = [
            'id',
            'name_uz',
            'name_ru',
            'name_uz_cyr',
            'category',
            'place',
            'rating',
        ]
        list_serializer_class = BaseBulkListSerializer


    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['place'] = instance.place.house_number if instance.place else None
        data['category'] = instance.category.name_uz if instance.category else None
        return data

    def validate(self, data):
        data = BaseNameValidationSerializer.validate(self, data)
        return data
