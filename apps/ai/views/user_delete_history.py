from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import DestroyAPIView
from rest_framework.exceptions import PermissionDenied

from ..models import QueryHistory
from ..serializers import QueryHistorySerializer


class UserDeleteHistoryView(DestroyAPIView):

    permission_classes = [IsAuthenticated, ]
    serializer_class = QueryHistorySerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return QueryHistory.objects.none()

        user = self.request.user
        if not user.is_authenticated:
            return QueryHistory.objects.none()  # or raise PermissionDenied()

        return QueryHistory.objects.filter(user=user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can not delete history which is yours!")
        instance.delete()