from rest_framework import serializers

from apps.users.models.user import User


class ForgotPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        phone_number = attrs['phone_number'].lower()
        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            raise serializers.ValidationError("User not found.")
        attrs['user'] = user
        return attrs
