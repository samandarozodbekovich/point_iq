from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from ..models import QueryHistory
from ..serializers import QueryHistorySerializer


class _UserHistoryMixin:
    permission_classes = [IsAuthenticated,]
    serializer_class = QueryHistorySerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return QueryHistory.objects.none()  # response empty queryset
        # Only the caller's own history.
        return QueryHistory.objects.filter(user=self.request.user).order_by("-created_at")


# Two views instead of one class inheriting ListAPIView and RetrieveAPIView:
# both define get(), and by MRO ListAPIView's always won, so history/<pk>/
# returned the whole list instead of one entry.
class UserHistoryView(_UserHistoryMixin, ListAPIView):
    pass


class UserHistoryDetailView(_UserHistoryMixin, RetrieveAPIView):
    pass
