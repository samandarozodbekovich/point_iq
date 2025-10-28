from apps.citizens.population.models import Population
from apps.citizens.population.serializers import PopulationSerializer
from apps.dictionary.views import BaseModelViewSet


class PopulationViewSet(BaseModelViewSet):
    model = Population
    serializer_class = PopulationSerializer