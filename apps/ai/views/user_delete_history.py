from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import DestroyAPIView
from rest_framework.exceptions import PermissionDenied

from ..models import QueryHistory
from ..serializers import QueryHistorySerializer


class UserDeleteHistoryView(DestroyAPIView):
    """Foydalanuvchi o'z so'rovlarini o'chirish"""
    permission_classes = [IsAuthenticated]
    serializer_class = QueryHistorySerializer

    def get_queryset(self):
        return QueryHistory.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("Sizga tegishli bo'lmagan tarixni o'chira olmaysiz.")
        instance.delete()