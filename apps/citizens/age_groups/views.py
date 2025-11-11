
from apps.citizens.age_groups.models import AgeGroup, AgeGroupPopulation
from apps.citizens.age_groups.serializers import AgeGroupSerializer, AgeGroupPopulationSerializer
from apps.shared.views.base_view_set import BaseModelViewSet


class AgeGroupViewSet(BaseModelViewSet):
    model = AgeGroup
    serializer_class = AgeGroupSerializer



class AgeGroupPopulationViewSet(BaseModelViewSet):
    model = AgeGroupPopulation
    serializer_class = AgeGroupPopulationSerializer
