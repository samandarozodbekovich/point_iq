from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.exceptions import ValidationError
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from apps.users.models.user import CODE_VERIFIED, NEW
from apps.users.serializers.verify import VerifySerializer

class VerifyAPIView(APIView):
    permission_classes = [IsAuthenticated]

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
        verifies = user.verify_codes.filter(
            expiration_time__gte=timezone.now(),
            code=code,
            is_confirmed=False
        )

        if not verifies.exists():
            raise ValidationError({
                "success": False,
                "message": "Invalid or expired verification code."
            })

        verifies.update(is_confirmed=True)

        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.is_verified = True
            user.save()
