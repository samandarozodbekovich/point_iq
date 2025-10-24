from rest_framework import serializers
from .base_bulk_list import BaseBulkListSerializer


class BaseBulkSerializer(serializers.ModelSerializer):

    def passes_test(self):
        test = self.context['request'].method in ('PUT', 'PATCH')
        test &= self.context.get('bulk_update', False)
        return test

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)

        if self.passes_test() and 'id' in data:
            ret['id'] = data.get('id')
        return ret

    class Meta:
        list_serializer_class = BaseBulkListSerializer