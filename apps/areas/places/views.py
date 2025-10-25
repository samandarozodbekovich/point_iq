from rest_framework import viewsets, permissions

from apps.areas.places.models import Place
from apps.areas.places.serializers import PlaceSerializer


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer

    def get_queryset(self):
        if self.action in ['list', 'create']:
            return Place.objects.all()
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return Place.objects.filter(id=self.kwargs['pk'])
        return Place.objects.none()

    def get_permissions(self):

        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]