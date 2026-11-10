from rest_framework import serializers
from .models import Competitor
from ..competitor_review.serializers import CompetitorReviewSerializer


class CompetitorSerializer(serializers.ModelSerializer):
    """Expects CompetitorViewSet.get_queryset(): category, reviews (with
    users) and hit counts are loaded up front, so no field queries per row.
    average_rating and review_count are the stored fields that the review
    signal keeps up to date.
    """
    reviews = CompetitorReviewSerializer(many=True, read_only=True)
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

    def get_hits(self, obj):
        # Read through the prefetched relation. HitCount.get_for_object()
        # cost a query per row and created a row when missing, so merely
        # listing competitors wrote to the database.
        hitcount = next(iter(obj.hit_count_generic.all()), None)
        return hitcount.hits if hitcount else 0


class CompetitorAnalysisSerializer(serializers.Serializer):
    category_id = serializers.IntegerField(required=True)
    lat = serializers.FloatField(help_text="Latitude", min_value=-90, max_value=90)
    long = serializers.FloatField(help_text="Longitude", min_value=-180, max_value=180)
    radius = serializers.ChoiceField(choices=[300, 500, 1000], default=300)



class LocationScoreSerializer(serializers.Serializer):
    lat = serializers.FloatField(min_value=-90, max_value=90)
    lon = serializers.FloatField(min_value=-180, max_value=180)
    potential_rent = serializers.FloatField(required=False, allow_null=True)