
from rest_framework import status
from rest_framework.response import Response

from .models import CompetitorCategory
from .serializers import CompetitorCategorySerializer
from ...shared.views.base_view_set import BaseModelViewSet


class CompetitorCategoryViewSet(BaseModelViewSet):

    model = CompetitorCategory
    serializer_class = CompetitorCategorySerializer

    def list(self, request, *args, **kwargs):
        lang = request.GET.get('lang', 'uz')
        queryset = self.get_queryset()
        data = []
        for category in queryset:
            data.append({
                'id': category.id,
                'name': getattr(category, f'name_{lang}', category.name_uz),
                'external_id': category.external_id
            })
        return Response(data, status=status.HTTP_200_OK)


