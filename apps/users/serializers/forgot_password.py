from rest_framework import serializers

from apps.users.models.user import DONE, User


class ForgotPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        phone_number = attrs['phone_number'].strip().lower()
        # No "user not found" error: the response must look the same either
        # way, or this endpoint tells anyone which numbers are registered.
        # Only finished accounts can reset; others complete signup instead.
        attrs['user'] = User.objects.filter(phone_number=phone_number, auth_status=DONE).first()
        return attrs
