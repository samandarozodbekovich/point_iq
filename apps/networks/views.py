from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .models import CellTower
from .serializers import CellTowerSerializer
from ..shared.views.base_view_set import BaseModelViewSet

# Yangi servisni import qilamiz
from apps.ai.services.ai_engine import BusinessAgent

class CellTowerViewSet(BaseModelViewSet):
    model = CellTower
    queryset = CellTower.objects.all()
    serializer_class = CellTowerSerializer

    @action(detail=False, methods=['get'])
    def ai_query(self, request):
        """
        GET /networks/ai_query/?query=<so'rov>
        Yangi BusinessAgent servisi orqali tahlil qilish.
        """
        query = request.query_params.get('query', '').strip()

        if not query:
            return Response(
                {"error": "query parametri yuborilmadi"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Barcha mantiq (Geocode, Stats, AI, History) bitta servisda
        # BusinessAgent ichida allaqachon extract_context va geocoding bor
        ai_response = BusinessAgent.ask_ai(
            query=query,
            user=request.user
        )

        # Yakuniy natija
        return Response(ai_response, status=status.HTTP_200_OK)