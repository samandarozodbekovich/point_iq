from rest_framework.generics import ListAPIView, RetrieveAPIView

from apps.citizens.relationship_status.models import RelationshipStatus, RelationshipStatusPopulation
from apps.citizens.relationship_status.serializers import RelationshipStatusSerializer, \
    RelationshipStatusPopulationSerializer


class RelationshipStatusAPIView(ListAPIView, RetrieveAPIView):
    serializer_class = RelationshipStatusSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        if pk:
            return RelationshipStatus.objects.filter(pk=pk)
        return RelationshipStatus.objects.all()

class RelationshipStatusPopulationAPIView(ListAPIView, RetrieveAPIView):
    serializer_class = RelationshipStatusPopulationSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        if pk:
            return RelationshipStatusPopulation.objects.filter(pk=pk)
        return RelationshipStatusPopulation.objects.all()