from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions
from rest_framework.exceptions import NotFound
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response

from apps.users.models import User
from apps.users.serializers.reset_password import ResetPasswordSerializer


class ResetPasswordView(UpdateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ResetPasswordSerializer
    http_method_names = ['put', 'patch']

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        user = self.get_object()

        return Response({
            'success': True,
            'message': "Password reset successful",
            "access": user.token()['access'],
            "refresh": user.token()['refresh'],
        })

