from rest_framework import serializers

from apps.areas.districts.models import District
from apps.citizens.people_consume.models import PeopleConsume

class PeopleConsumeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all())

    class Meta:
        model = PeopleConsume
        fields = [
            'id',
            'district',
            'month',
            'year',
            'consume_gas',
            'consume_electric',
            'bus_station',
        ]
        read_only_fields = ('created_at', 'updated_at')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['district'] = instance.district.name_uz if instance.district else None
        return data
