from apps.citizens.age_groups.models import AgeGroup
from apps.citizens.age_groups.serializers import AgeGroupSerializer
from apps.dictionary.views.base_model_view_set import BaseModelViewSet


class AgeGroupViewSet(BaseModelViewSet):
    model = AgeGroup
    serializer_class = AgeGroupSerializer


