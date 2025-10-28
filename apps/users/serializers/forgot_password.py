from rest_framework import serializers

from apps.users.models.user import User


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs['email'].lower()
        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("User not found.")
        attrs['user'] = user
        return attrs
