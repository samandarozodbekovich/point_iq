from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .models import CellTower
from .serializers import CellTowerSerializer
from ..shared.views.base_view_set import BaseModelViewSet

from apps.ai.services.ai_engine import BusinessAgent

class CellTowerViewSet(BaseModelViewSet):
    model = CellTower
    queryset = CellTower.objects.all()
    serializer_class = CellTowerSerializer

    @action(detail=False, methods=['get'])
    def ai_query(self, request):
        """
        GET /networks/ai_query/?query=<text>
        Analysis through the BusinessAgent service.
        """
        query = request.query_params.get('query', '').strip()

        if not query:
            return Response(
                {"error": "query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Geocoding, stats, AI and history all live in BusinessAgent.
        ai_response = BusinessAgent.ask_ai(
            query=query,
            user=request.user
        )

        # Yakuniy natija
        return Response(ai_response, status=status.HTTP_200_OK)