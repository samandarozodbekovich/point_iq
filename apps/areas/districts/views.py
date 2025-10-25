from rest_framework import viewsets, permissions
from rest_framework.decorators import action

from apps.areas.districts.models import District
from apps.areas.districts.serializers import DistrictSerializer


class DistrictViewSet(viewsets.ModelViewSet):
    serializer_class = DistrictSerializer
    queryset = District.objects.all()

    def get_queryset(self):
        if self.action in ['list', 'create']:
            return District.objects.all()
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return District.objects.filter(id=self.kwargs['pk'])
        return District.objects.none()

    def get_permissions(self):

        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
