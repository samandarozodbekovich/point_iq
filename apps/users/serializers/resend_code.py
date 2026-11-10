from django.db import transaction
from rest_framework import serializers

from apps.users.models.user import DONE, User
from apps.users.tasks import send_registration_email

class ResendCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)

    def validate(self, data):
        phone_number = data.get("phone_number").lower()
        user = User.objects.filter(phone_number=phone_number).first()

        if not user:
            raise serializers.ValidationError("This user does not exist.")
        if user.auth_status == DONE:
            raise serializers.ValidationError("This phone number is already verified.")
        data["user"] = user
        return data

    def save(self, **kwargs):
        user = self.validated_data["user"]
        code = user.create_verify_code()
        # code will be sent to phone_number when service works
        transaction.on_commit(lambda: send_registration_email.delay(user.phone_number, code))
        return user