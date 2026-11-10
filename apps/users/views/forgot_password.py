from django.db import transaction
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.shared.throttles import OTPSendThrottle
from apps.users.serializers.forgot_password import ForgotPasswordSerializer
from apps.users.tasks import send_registration_email


class ForgotPasswordView(APIView):
    """Step 1 of password reset: send a code to the phone.

    Step 2 is reset-password with phone_number + code + new password.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_classes = [OTPSendThrottle]
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get('user')
        if user is not None:
            code = user.create_verify_code()
            transaction.on_commit(lambda: send_registration_email.delay(user.phone_number, code))

        # Same answer whether or not the number is registered.
        return Response({
            'success': True,
            'message': 'If this number is registered, a verification code has been sent.',
        }, status=200)
