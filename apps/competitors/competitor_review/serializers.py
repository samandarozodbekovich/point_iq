from rest_framework import serializers

from apps.competitors.competitor_review.models import CompetitorReview


class CompetitorReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CompetitorReview
        fields = '__all__'

