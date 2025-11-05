from rest_framework.generics import ListAPIView, RetrieveAPIView

from apps.citizens.population.models import Population
from apps.citizens.population.serializers import PopulationSerializer


class PopulationAPIView(ListAPIView, RetrieveAPIView):
    serializer_class = PopulationSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        if pk:
            return Population.objects.filter(pk=pk)
        return Population.objects.all()