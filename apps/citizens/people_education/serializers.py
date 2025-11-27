from rest_framework import serializers

from apps.areas.districts.models import District
from apps.citizens.people_education.models import PeopleEducation


class PeopleEducationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all())

    class Meta:
        model = PeopleEducation
        fields = [
            'id',
            'district',
            'regional_school',
            'regional_kindergarten',
            'regional_teachers',
            'regional_students',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['district'] = instance.district.name_uz if instance.district else None
        return data
