from rest_framework import serializers


class BaseBulkListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        model = self.child.Meta.model
        objs = [model(**item) for item in validated_data]
        return model.objects.bulk_create(objs)

    def update(self, instances, validated_data):
        model = self.child.Meta.model
        instance_mapping = {obj.id: obj for obj in instances}
        update_objs = []

        for item in validated_data:
            obj = instance_mapping.get(item.get('id'))
            for field, value in item.items():
                setattr(obj, field, value)
            update_objs.append(obj)

        fields = list(validated_data[0].keys())
        model.objects.bulk_update(update_objs, fields=fields)
        return update_objs