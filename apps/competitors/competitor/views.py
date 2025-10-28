from apps.dictionary.views.base_model_view_set import BaseModelViewSet
from .serializers import CompetitorSerializer
from .models import Competitor


class CompetitorViewSet(BaseModelViewSet):
    model = Competitor
    serializer_class = CompetitorSerializer



