from rest_framework import permissions
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response

from apps.users.serializers.change_user_info import ChangeUserInformation
from apps.users.models.user import User

class ChangeUserInfoView(UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ChangeUserInformation
    http_method_names = ["put", 'patch']

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            'success': True,
            'message': 'User info updated successfully',
            'auth_status': request.user.auth_status,
        })

    def get_object(self):
        return self.request.user

