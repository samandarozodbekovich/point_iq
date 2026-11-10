from rest_framework import viewsets, permissions

class BaseModelViewSet(viewsets.ModelViewSet):

    model = None
    serializer_class = None

    def get_queryset(self):
        if self.model is None:
            raise ValueError("BaseModelViewSet uchun 'model' atributi belgilanmagan.")

        # The same queryset for every action: get_object() already narrows it
        # to the requested pk. Returning none() for actions missing from a
        # list (destroy, custom detail actions) made them all answer 404.
        return self.model.objects.all()

    def get_permissions(self):
        # Deny by default: reads are public, every write is admin-only.
        # Listing write actions by name missed extra ones such as
        # BaseBulkMethods.bulk_create/bulk_update, which were left open.
        if self.request.method in permissions.SAFE_METHODS:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    
