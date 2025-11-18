from rest_framework import serializers

from .models import Population


class PopulationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Population
        fields = [
            'id',
            'district',
            'count_male',
            'count_female',
            'average_income',
            'unemployment_rate',
            'population_density',
            'birth_rate',
            'death_rate',
            'immigration_count',
            'emission_count',
        ]


    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['district'] = instance.district.name_uz if instance.district else None
        return data
