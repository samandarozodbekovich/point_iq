from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.password_validation import validate_password

from apps.users.models.user import CODE_VERIFIED, DONE

class ChangeUserInformation(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        # Registration can only be completed after the phone code is confirmed.
        if self.instance is None or self.instance.auth_status != CODE_VERIFIED:
            raise PermissionDenied("Verify your phone number before completing registration.")
        if data['password'] != data['confirm_password']:
            raise ValidationError("Passwords do not match.")
        validate_password(data['password'])
        return data

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name')
        instance.last_name = validated_data.get('last_name')
        instance.set_password(validated_data.get('password'))
        instance.auth_status = DONE
        instance.save()
        return instance
