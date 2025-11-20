from rest_framework import serializers

from apps.government_bodies.models.government_body import GovernmentBody
from apps.shared.serializers import BaseNameValidationSerializer


class GovernmentBodySerializer(serializers.ModelSerializer):
    name_field = ['name_uz', 'name_ru', 'name_uz_cyr']

    class Meta:
        model = GovernmentBody
        fields = [
            'id',
            'name_uz',
            'name_ru',
            'name_uz_cyr',
            'description',
            'address',
            'schedule',
            'director',
            'phone_number',
            'email',
            'latitude',
            'longitude',
        ]
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def validate(self, data):
        data = BaseNameValidationSerializer.validate(self, data)
        return data