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
        super().update(request, *args, **kwargs)
        user = request.user
        # Setting the password invalidates the signup token (CHECK_REVOKE_TOKEN),
        # so hand back fresh tokens; otherwise the client would be logged out.
        user.revoke_tokens()
        tokens = user.token()
        return Response({
            'success': True,
            'message': 'User info updated successfully',
            'auth_status': user.auth_status,
            'access': tokens['access'],
            'refresh': tokens['refresh'],
        })

    def get_object(self):
        return self.request.user
