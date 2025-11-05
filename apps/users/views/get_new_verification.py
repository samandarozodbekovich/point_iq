from datetime import datetime, timezone

from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView


class GetNewVerificationView(APIView):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        self.check_verification(user)
        code = user.create_verify_code('phone_number')

        return Response({"code": code})

    @staticmethod
    def check_verification(user):
        verifies = user.verify_codes.filter(
            expiration_time__gt=timezone.now(),
            is_confirmed=False
        )
        if verifies.exists():
            raise ValidationError(
                "Verification code is already in use",
            )
