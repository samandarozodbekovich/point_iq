from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.models.user import DONE


class LoginSerializer(TokenObtainPairSerializer):
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number').lower()
        password = attrs.get('password')

        user = authenticate(phone_number=phone_number, password=password)
        if not user:
            raise ValidationError("Phone number or password is incorrect.")

        if user.auth_status != DONE:
            raise PermissionDenied("You are not authorized to log in yet.")

        token_data = user.token()
        token_data['auth_status'] = user.auth_status
        return token_data
