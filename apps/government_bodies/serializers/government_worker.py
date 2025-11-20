from rest_framework import serializers

from apps.government_bodies.models import GovernmentWorker
from apps.shared.serializers import BaseNameValidationSerializer


class GovernmentWorkerSerializer(serializers.ModelSerializer):
    name_field = ['name_uz', 'name_ru', 'name_uz_cyr']

    class Meta:
        model = GovernmentWorker
        fields = [
            'id',
            'government',
            'name_uz',
            'name_ru',
            'name_uz_cyr',
            'position',
            'phone_number',
            'work_day',
            'work_time',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def validate(self, data):
        data = BaseNameValidationSerializer.validate(self, data)
        return data
