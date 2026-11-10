from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers.logout import LogoutSerializer


class LogoutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        invalid = Response(
            {'success': False, 'message': 'Invalid or expired refresh token.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

        # Only token errors are expected here; anything else is a real bug
        # and should surface as one instead of a quiet 200.
        try:
            token = RefreshToken(serializer.validated_data['refresh'])
        except TokenError:
            return invalid

        # A user may only end their own session.
        if str(token.get(api_settings.USER_ID_CLAIM)) != str(request.user.pk):
            return invalid

        token.blacklist()
        return Response({'success': True, 'message': 'Successfully logged out'})
