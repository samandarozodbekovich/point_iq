from rest_framework.decorators import action
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status

class BaseBulkMethods:

    @action(detail=False, methods=['post'])
    def bulk_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        model = self.get_queryset().model

        with transaction.atomic():
            model.objects.bulk_create([
                model(**item) for item in serializer.validated_data
            ])
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['put'])
    def bulk_update(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        context['bulk_update'] = True

        serializer = self.get_serializer(data=request.data, many=True, context=context)
        serializer.is_valid(raise_exception=True)

        model = self.get_queryset().model
        update_objs = []

        update_fields = [f for f, field in serializer.fields.keys()
                         if f != 'id' and not field.read_only
                         ]

        with transaction.atomic():
            for item in serializer.validated_data:
                try:
                    obj = model.objects.get(id=item['id'])
                except model.DoesNotExist:
                    return Response(
                        {'error': f"Object with id {item[id]} not found"}
                    )

                for field, value in item.items():
                    setattr(obj, field, value)
                update_objs.append(obj)
            fields = list(serializer.validated_data[0].keys())
            model.objects.bulk_update(update_objs, fields=fields)
        return Response(
            serializer.data
        )
