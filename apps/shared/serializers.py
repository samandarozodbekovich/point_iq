from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class BaseNameValidationSerializer(serializers.ModelSerializer):
    name_field = None

    def validate(self, data):
        name_field = self.name_field
        model = self.Meta.model

        name = data.get(name_field, None)
        if name is None:
            raise ValidationError("Name field is required")

        name = name.replace(' ', '').replace('_', '')

        if model.objects.filter(**{name_field: name}).exists():
            raise ValidationError("Name already exists")
        return data
