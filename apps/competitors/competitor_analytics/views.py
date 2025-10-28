from apps.dictionary.views.base_model_view_set import BaseModelViewSet
from .models import CompetitorAnalytics
from .serializers import CompetitorAnalyticsSerializer


class CompetitorAnalyticsViewSet(BaseModelViewSet):
    model = CompetitorAnalytics
    serializer_class = CompetitorAnalyticsSerializer



