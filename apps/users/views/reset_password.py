from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.shared.throttles import OTPVerifyThrottle
from apps.users.serializers.reset_password import ResetPasswordSerializer


class ResetPasswordView(APIView):
    """Step 2 of password reset (step 1 is forgot-password).

    Anonymous on purpose: the user has no token yet. Possession of the phone
    is proven by the code, which consume_code checks with attempt limits.
    """
    permission_classes = (permissions.AllowAny,)
    authentication_classes = []
    throttle_classes = [OTPVerifyThrottle]

    @swagger_auto_schema(request_body=ResetPasswordSerializer)
    def put(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokens = user.token()
        return Response({
            'success': True,
            'message': "Password reset successful",
            "access": tokens['access'],
            "refresh": tokens['refresh'],
        })

    @swagger_auto_schema(request_body=ResetPasswordSerializer)
    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)
