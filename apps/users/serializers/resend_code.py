from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.users.models.user import User, NEW, CODE_VERIFIED, DONE
from apps.users.tasks import send_registration_email

class ResendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, data):
        email = data.get("email").lower()
        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError("This user does not exist.")
        if user.auth_status == 'done':
            raise serializers.ValidationError("This email is already verified.")
        data["user"] = user
        return data

    def save(self, **kwargs):
        user = self.validated_data["user"]
        code = user.create_verify_code()
        transaction.on_commit(lambda: send_registration_email.delay(user.email, code))
        return user

