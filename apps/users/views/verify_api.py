from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from apps.shared.throttles import OTPVerifyThrottle
from apps.users.models.user import CODE_VERIFIED, NEW
from apps.users.otp import consume_code
from apps.users.serializers.verify import VerifySerializer

class VerifyAPIView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [OTPVerifyThrottle]

    @swagger_auto_schema(
        request_body=VerifySerializer,
        responses={
            200: openapi.Response(description="Verification successful"),
            400: "Validation error",
            401: "Unauthorized",
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = VerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        code = serializer.validated_data['code']

        self.check_verify(user, code)

        tokens = user.token()
        return Response({
            'success': True,
            'auth_status': user.auth_status,
            'access': tokens.get('access'),
            'refresh': tokens.get('refresh'),
        })



    @staticmethod
    def check_verify(user, code):
        consume_code(user, code)

        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.is_verified = True
            user.save()
