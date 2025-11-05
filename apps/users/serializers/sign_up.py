from rest_framework import serializers

from apps.users.models.user import User
from apps.users.signals import send_activation_email


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone_number',)

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError('This phone number is already registered.')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(phone_number=validated_data['phone_number'])
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update(instance.token())
        return data