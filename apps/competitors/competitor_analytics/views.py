from apps.shared.views.base_view_set import BaseModelViewSet
from .models import CompetitorAnalytics
from .serializers import CompetitorAnalyticsSerializer
from ...core.views import BaseBulkMethods


class CompetitorAnalyticsViewSet(BaseBulkMethods, BaseModelViewSet):
    model = CompetitorAnalytics
    serializer_class = CompetitorAnalyticsSerializer



