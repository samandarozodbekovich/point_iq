# apps/competitors/views.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from apps.competitors.utils import search_places_with_geocode


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CompetitorSearchAPIView(APIView):

    def get(self, request, *args, **kwargs):
        city = request.GET.get("city")
        category = request.GET.get("category")

        if not city:
            return Response({"error": "city parametri kerak"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not category:
            return Response({"error": "category parametri kerak"},
                            status=status.HTTP_400_BAD_REQUEST)

        results = search_places_with_geocode(city, category)

        return Response({
            "category": category,
            "results": results
        }, status=status.HTTP_200_OK)