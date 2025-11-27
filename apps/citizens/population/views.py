from apps.citizens.population.models import Population
from apps.citizens.population.serializers import PopulationSerializer
from apps.core.views import BaseBulkMethods
from apps.shared.views.base_view_set import BaseModelViewSet


class PopulationViewSet(BaseModelViewSet, BaseBulkMethods):
    model = Population
    serializer_class = PopulationSerializer
