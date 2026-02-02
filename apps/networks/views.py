
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CellTower
from .serializers import CellTowerSerializer
from apps.ai.ai_utils import build_vector_db, query_ai
from ..shared.views.base_view_set import BaseModelViewSet

index, tower_ids, peopleconsume_data, peopleeducation_data = None, None, None, None

class CellTowerViewSet(BaseModelViewSet):
    model = CellTower
    queryset = CellTower.objects.all()
    serializer_class = CellTowerSerializer

    @action(detail=False, methods=['get'])
    def ai_query(self, request):
        """
        GET /networks/ai_query/?query=<so'rov>
        """
        global index, tower_ids, peopleconsume_data, peopleeducation_data

        # Query parametrini tekshirish
        query = request.query_params.get('query', None)
        if not query:
            return Response({"error": "query parameter required"}, status=400)

        # Vector DB yaratish (agar hali yo'q bo'lsa)
        if index is None or tower_ids is None:
            try:
                index, tower_ids, peopleconsume_data, peopleeducation_data = build_vector_db()
            except Exception as e:
                return Response({"error": f"Vector DB yaratishda xatolik: {e}"}, status=500)

        # AI so‘rovini qaytarish
        answer = query_ai(query, index, tower_ids, peopleconsume_data, peopleeducation_data)
        return Response({"query": query, "answer": answer})





