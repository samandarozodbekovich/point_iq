from rest_framework import serializers
from .models import Competitor

class CompetitorSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Competitor
        fields = [
            "id",
            "name_uz",
            "name_ru",
            "name_uz_cyr",
            "address",
            "longitude",
            "latitude",
            "rating",
            "category",
            "footfall_estimate",
            "review_count",
        ]

    def get_category(self, obj):
        if obj.category:
            return {
                "id": obj.category.id,
                "name_uz": obj.category.name_uz,
                "name_ru": obj.category.name_ru,
                "name_uz_cyr": obj.category.name_uz_cyr,
                "external_id": obj.category.external_id,
            }
        return None
