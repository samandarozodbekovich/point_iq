from apps.dictionary.views.base_model_view_set import BaseModelViewSet
from .models import CompetitorCategory
from .serializers import CompetitorCategorySerializer


class CompetitorCategoryViewSet(BaseModelViewSet):
    model = CompetitorCategory
    serializer_class = CompetitorCategorySerializer



