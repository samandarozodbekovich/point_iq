from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.users.models.user import DONE, OTP_LENGTH, User
from apps.users.otp import consume_code, invalid_code_error


class ResetPasswordSerializer(serializers.Serializer):
    """Step 2 of password reset: prove phone ownership with the code and set a new password."""
    phone_number = serializers.CharField(write_only=True, required=True)
    code = serializers.CharField(min_length=OTP_LENGTH, max_length=OTP_LENGTH, write_only=True, required=True)
    password = serializers.CharField(min_length=8, write_only=True, required=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True, required=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords must match.")

        user = User.objects.filter(
            phone_number=data['phone_number'].strip().lower(), auth_status=DONE
        ).first()
        if user is None:
            # Same error as a wrong code, so the number's existence isn't revealed.
            raise invalid_code_error()

        # Check the password before the code, so a rejected password
        # doesn't burn one of the user's code attempts.
        validate_password(data['password'], user)
        consume_code(user, data['code'])

        data['user'] = user
        return data

    def save(self, **kwargs):
        user = self.validated_data['user']
        user.set_password(self.validated_data['password'])
        user.save()
        return user
