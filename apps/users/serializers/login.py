from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class LoginSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email').lower()
        password = attrs.get('password')

        user = authenticate(email=email, password=password)
        if not user:
            raise ValidationError("Email or password is incorrect.")

        if user.auth_status != 'done':
            raise PermissionDenied("You are not authorized to log in yet.")

        token_data = user.token()
        token_data['auth_status'] = user.auth_status
        return token_data
