from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser

from apps.areas.cities.models import City
from apps.areas.cities.serializers import CitySerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def get_queryset(self):
        if self.action in ['list', 'create']:
            return City.objects.all()
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return City.objects.filter(id=self.kwargs['pk'])
        return City.objects.none()

    def get_permissions(self):

        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser,]
        else:
            permission_classes = [AllowAny,]
        return [permission() for permission in permission_classes]