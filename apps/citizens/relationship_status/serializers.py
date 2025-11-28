from rest_framework import serializers

from .models import RelationshipStatus, RelationshipStatusPopulation
from ...shared.serializers import BaseNameValidationSerializer


class RelationshipStatusSerializer(BaseNameValidationSerializer):

    name_field = ['name_uz', 'name_ru', 'name_cyr']

    class Meta:
        model = RelationshipStatus
        fields = [
            'id',
            'name_uz',
            'name_ru',
            'name_cyr',
        ]


    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def validate(self, data):
        data = BaseNameValidationSerializer.validate(self, data)
        return data

class RelationshipStatusPopulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelationshipStatusPopulation
        fields = [
            'id',
            'population',
            'relationship_status',
            'count'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['population'] = instance.population.population_density if instance.population else None
        data['relationship_status'] = instance.relationship_status.name_uz if instance.relationship_status else None
        return data

