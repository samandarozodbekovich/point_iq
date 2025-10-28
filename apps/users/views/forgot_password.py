
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.forgot_password import ForgotPasswordSerializer
from apps.users.tasks import send_registration_email


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get('user')
        code = user.create_verify_code('email')
        send_registration_email(user.email, code)

        return Response({
            'success': True,
            'message': 'Verification code sent to your email',
            'status': user.auth_status,
        }, status=200)


