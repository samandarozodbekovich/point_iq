from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.shared.throttles import OTPSendThrottle
from apps.users.tasks import send_registration_email


class GetNewVerificationView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [OTPSendThrottle]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        self.check_verification(user)
        code = user.create_verify_code()
        # The code goes only to the phone; returning it here would let anyone
        # holding a signup token skip phone verification.
        transaction.on_commit(lambda: send_registration_email.delay(user.phone_number, code))

        return Response({"success": True, "message": "Code sent successfully"})

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
