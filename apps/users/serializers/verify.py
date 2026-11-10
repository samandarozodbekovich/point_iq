# apps/users/serializers/verify.py
from rest_framework import serializers

from apps.users.models.user import OTP_LENGTH


class VerifySerializer(serializers.Serializer):
    code = serializers.CharField(
        min_length=OTP_LENGTH,
        max_length=OTP_LENGTH,
        required=True
    )
