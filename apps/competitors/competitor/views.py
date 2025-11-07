from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.competitors.competitor.models import Competitor
from apps.competitors.competitor.serializers import CompetitorSerializer

from .tasks import fetch_and_update_competitors

class CompetitorViewSet(viewsets.ModelViewSet):
    queryset = Competitor.objects.all()
    serializer_class = CompetitorSerializer

    @action(detail=False, methods=['get'])
    def fetch(self, request):
        city = request.query_params.get("city")
        category = request.query_params.get("category")
        if not city or not category:
            return Response({"error": "city and category required"}, status=status.HTTP_400_BAD_REQUEST)

        fetch_and_update_competitors.delay(city, category)
        return Response({"status": "fetch_started", "city": city, "category": category})
