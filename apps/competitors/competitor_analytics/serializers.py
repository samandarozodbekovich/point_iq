from apps.shared.serializers import BaseNameValidationSerializer
from .models import CompetitorAnalytics
from ...core.serializers.base_bulk_list import BaseBulkListSerializer


class CompetitorAnalyticsSerializer(BaseNameValidationSerializer):

    class Meta:
        model = CompetitorAnalytics
        fields = [
            'id',
            'competitor',
            'date_recorded',
            'footfall_estimate',
            'average_rating',
            'review_count',
        ]
        list_serializer_class = BaseBulkListSerializer


    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['competitor'] = instance.competitor.name_uz if instance.competitor else None
        return data

    def validate(self, data):
        data = BaseNameValidationSerializer.validate(self, data)
        return data
