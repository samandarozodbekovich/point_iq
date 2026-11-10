
from rest_framework import status
from rest_framework.response import Response

from .models import CompetitorCategory
from .serializers import CompetitorCategorySerializer
from ...shared.views.base_view_set import BaseModelViewSet

LANGUAGES = ('uz', 'ru', 'cyr')


class CompetitorCategoryViewSet(BaseModelViewSet):

    model = CompetitorCategory
    serializer_class = CompetitorCategorySerializer

    def list(self, request, *args, **kwargs):
        lang = request.GET.get('lang', 'uz')
        if lang not in LANGUAGES:
            lang = 'uz'
        queryset = self.get_queryset()
        data = []
        for category in queryset:
            data.append({
                'id': category.id,
                'name': getattr(category, f'name_{lang}'),
                # external_id (a Foursquare category id) was replaced by
                # google_type when search moved to Google Places (migration 0004).
                'google_type': category.google_type,
            })
        return Response(data, status=status.HTTP_200_OK)
