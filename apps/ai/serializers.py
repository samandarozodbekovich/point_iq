
from rest_framework import serializers
from .models import QueryHistory

class QueryHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryHistory
        fields = [
            "id",
            'user',
            "user_query",
            "status",
            "response_json",
            "business_type",
            "region",
            "created_at"
        ]


class QueryHistoryCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = QueryHistory
        fields = ["user_query", "business_type", "region"]
        extra_kwargs = {
            "user_query": {"required": True},
            "business_type": {"required": False},
            "region": {"required": False},
        }
