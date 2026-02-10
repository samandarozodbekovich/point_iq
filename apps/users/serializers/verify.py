# apps/users/serializers/verify.py
from rest_framework import serializers

class VerifySerializer(serializers.Serializer):
    code = serializers.CharField(
        max_length=4,
        required=True
    )
