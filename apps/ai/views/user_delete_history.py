from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import DestroyAPIView
from rest_framework.exceptions import PermissionDenied

from ..models import QueryHistory
from ..serializers import QueryHistorySerializer


class UserDeleteHistoryView(DestroyAPIView):
<<<<<<< HEAD
    """Foydalanuvchi o'z so'rovlarini o'chirish"""
=======

>>>>>>> 7cb6155 (Initial clean commit)
    permission_classes = [IsAuthenticated, ]
    serializer_class = QueryHistorySerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
<<<<<<< HEAD
            # DRF-YASG uchun schema generation
=======
>>>>>>> 7cb6155 (Initial clean commit)
            return QueryHistory.objects.none()

        user = self.request.user
        if not user.is_authenticated:
            return QueryHistory.objects.none()  # yoki raise PermissionDenied()

        return QueryHistory.objects.filter(user=user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
<<<<<<< HEAD
            raise PermissionDenied("Sizga tegishli bo'lmagan tarixni o'chira olmaysiz.")
=======
            raise PermissionDenied("You can not delete history which is yours!")
>>>>>>> 7cb6155 (Initial clean commit)
        instance.delete()