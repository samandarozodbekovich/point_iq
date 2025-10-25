from rest_framework import viewsets, permissions

from apps.areas.streets.models import Street
from apps.areas.streets.serializers import StreetSerializer


class StreetViewSet(viewsets.ModelViewSet):
    serializer_class = StreetSerializer
    queryset = Street.objects.all()

    def get_queryset(self):
        if self.action in ['list', 'create']:
            return Street.objects.all()
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return Street.objects.filter(id=self.kwargs['pk'])
        return Street.objects.none()

    def get_permissions(self):

        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]