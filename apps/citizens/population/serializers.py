from rest_framework import serializers

from .models import Population


class PopulationSerializer(serializers.ModelSerializer):
    count_male = serializers.FloatField()
    count_female = serializers.FloatField()
    population_density = serializers.FloatField()
    average_income = serializers.FloatField()
    unemployment_rate = serializers.FloatField()
    birth_rate = serializers.FloatField()
    death_rate = serializers.FloatField()

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

    def validate(self, data):
        return data