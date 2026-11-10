from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import CellTower
from .serializers import CellTowerSerializer
from ..shared.throttles import AIThrottle
from ..shared.views.base_view_set import BaseModelViewSet

from apps.ai.services.ai_engine import BusinessAgent

class CellTowerViewSet(BaseModelViewSet):
    model = CellTower
    queryset = CellTower.objects.all()
    serializer_class = CellTowerSerializer

    # ai_query calls OpenAI like /api/ai/chat/. As a GET action it fell under
    # BaseModelViewSet's "reads are public" rule, so anyone could spend the
    # OpenAI quota through it, around the chat endpoint's login and limit.
    def get_permissions(self):
        if self.action == 'ai_query':
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_throttles(self):
        if self.action == 'ai_query':
            return [AIThrottle()]  # shares the chat endpoint's hourly budget
        return super().get_throttles()

    @action(detail=False, methods=['get'])
    def ai_query(self, request):
        """
        GET /networks/cell-towers/ai_query/?query=<text>
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

        return Response(ai_response, status=status.HTTP_200_OK)
