from rest_framework import serializers

from apps.users.models.user import User
from apps.users.signals import send_activation_email


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email',)

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already registered.')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(email=validated_data['email'])
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update(instance.token())
        return data