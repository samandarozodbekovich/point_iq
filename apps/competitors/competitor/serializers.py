from rest_framework import serializers

from apps.shared.serializers import BaseNameValidationSerializer
from .models import Competitor
from ...core.serializers.base_bulk_list import BaseBulkListSerializer


class CompetitorSerializer(serializers.ModelSerializer):
    place = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    name_field = ['name_uz', 'name_ru', 'name_uz_cyr']

    class Meta:
        model = Competitor
        fields = ["id", "name_uz", 'name_ru', 'name_uz_cyr',"place", "category"]

    def get_place(self, obj):
        if obj.place:
            return f"{obj.place.street} {obj.place.house_number or ''}"
        return None

    def get_category(self, obj):
        if obj.category:
            return obj.category.name_uz
        return None
