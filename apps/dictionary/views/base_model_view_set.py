from rest_framework import viewsets, permissions

class BaseModelViewSet(viewsets.ModelViewSet):

    model = None
    serializer_class = None

    def get_queryset(self):
        if self.model is None:
            raise ValueError("BaseModelViewSet uchun 'model' atributi belgilanmagan.")

        if self.action in ['list', 'create']:
            return self.model.objects.all()
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return self.model.objects.filter(id=self.kwargs.get('pk'))
        return self.model.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
