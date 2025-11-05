from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.users.models.user import User, NEW, CODE_VERIFIED, DONE
from apps.users.tasks import send_registration_email

class ResendCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)

    def validate(self, data):
        phone_number = data.get("phone_number").lower()
        user = User.objects.filter(email=phone_number).first()

        if not user:
            raise serializers.ValidationError("This user does not exist.")
        if user.auth_status == 'done':
            raise serializers.ValidationError("This email is already verified.")
        data["user"] = user
        return data

    def save(self, **kwargs):
        user = self.validated_data["user"]
        code = user.create_verify_code()
        # code will be sent to phone_number when service works
        transaction.on_commit(lambda: send_registration_email.delay(user.email, code))
        return user

