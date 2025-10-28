from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class BaseNameValidationSerializer(serializers.ModelSerializer):
    name_field = None

    def validate(self, data):
        model = self.Meta.model
        name_fields = self.name_field

        instance = getattr(self, "instance", None)

        for field in name_fields:
            name = data.get(field)
            if not name:
                continue

            cleaned_name = name.replace(' ', '').replace('_', '')

            queryset = model.objects.filter(**{field: cleaned_name})
            if instance:
                queryset = queryset.exclude(pk=instance.pk)

            if queryset.exists():
                raise ValidationError({field: "This name already exists"})

        return data


