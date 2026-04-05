from django.db import models
from hitcount.models import HitCount
from rest_framework import serializers
from .models import Competitor
from ..competitor_review.serializers import CompetitorReviewSerializer


class CompetitorSerializer(serializers.ModelSerializer):
    reviews = CompetitorReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    hits = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Competitor
        fields = [
            "id",
            "name_uz",
            "name_ru",
            "name_cyr",
            "address",
            "longitude",
            "latitude",
            'external_id',
            'google_place_id',
            'schedule_from',
            'schedule_to',
            "category",
            "footfall_estimate",
            "review_count",
            'average_rating',
            'hits',
            'reviews',
        ]

    def get_category(self, obj):
        if obj.category:
            return {
                "id": obj.category.id,
                "name_uz": obj.category.name_uz,
                "name_ru": obj.category.name_ru,
                "name_cyr": obj.category.name_cyr,
                "google_type": getattr(obj.category, 'google_type', None),
            }
        return None

    def get_average_rating(self, obj):
        avg = obj.reviews.aggregate(models.Avg('rating'))['rating__avg']
        return round(avg, 2) if avg else None

    def get_hits(self, obj):
        hitcount = HitCount.objects.get_for_object(obj)
        return hitcount.hits


class CompetitorAnalysisSerializer(serializers.Serializer):
    category_id = serializers.IntegerField(required=True)
    lat = serializers.FloatField(help_text="Latitude", min_value=-90, max_value=90)
    long = serializers.FloatField(help_text="Longitude", min_value=-180, max_value=180)
    radius = serializers.ChoiceField(choices=[300, 500, 1000], default=300)



class LocationScoreSerializer(serializers.Serializer):
    lat = serializers.FloatField(min_value=-90, max_value=90)
    lon = serializers.FloatField(min_value=-180, max_value=180)
    potential_rent = serializers.FloatField(required=False, allow_null=True)