from rest_framework.views import APIView
from rest_framework.response import Response
from apps.ai.services.ai_engine import BusinessAgent


class UniversalAIView(APIView):
    def post(self, request):
        query = request.data.get("query", "").strip()

        response_data = BusinessAgent.ask_ai(query=query, user=request.user)

        return Response(response_data)