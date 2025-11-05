from rest_framework.response import Response
from rest_framework.views import APIView

from apps.competitors.competitor.models import Competitor
from apps.competitors.competitor.views import StandardResultsSetPagination
from apps.competitors.competitor_categories.models import CompetitorCategory


class CompetitorCategoryAPIView(APIView):
    pagination_class = StandardResultsSetPagination

    def get(self, request, category_name):
        paginator = StandardResultsSetPagination()

        try:
            category = CompetitorCategory.objects.get(name_uz=category_name)
        except CompetitorCategory.DoesNotExist:
            return Response({"detail": "Category not found"}, status=404)

        queryset = Competitor.objects.filter(category=category).order_by('id')
        result_page = paginator.paginate_queryset(queryset, request)

        data = [{
            "id": c.id,
            "name": c.name_uz,
            "street": c.place.street.name_uz,
            "address": c.place.description,
            "latitude": c.place.latitude,
            "longitude": c.place.longitude
        } for c in result_page]

        return paginator.get_paginated_response({
            "category": category_name,
            "total_count": queryset.count(),
            "results": data
        })
