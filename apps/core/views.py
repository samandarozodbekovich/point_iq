from rest_framework.decorators import action
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status

class BaseBulkMethods:
    lang_fields = ['_uz', '_ru', '_uz_cyr']

    def get_lang_data(self, item):

        return [item]

    @action(detail=False, methods=['post'], url_path='create')
    def bulk_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        model = self.get_queryset().model

        created_objects = []

        with transaction.atomic():
            objects_to_create = []

            for item in serializer.validated_data:
                for li in self.get_lang_data(item):
                    obj = model(**li)
                    objects_to_create.append(obj)

            if objects_to_create:
                model.objects.bulk_create(objects_to_create, ignore_conflicts=True)
                created_objects = objects_to_create  # keyin serialize qilamiz

        return Response(self.get_serializer(created_objects, many=True).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['put', 'patch'], url_path='update')
    def bulk_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        model = self.get_queryset().model
        update_objs = []

        with transaction.atomic():
            for item in serializer.validated_data:
                obj_id = item.get('id')
                if not obj_id:
                    return Response({'error': 'ID missing in item'}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    obj = model.objects.get(id=obj_id)
                except model.DoesNotExist:
                    return Response({'error': f"Object with id {obj_id} not found"}, status=status.HTTP_404_NOT_FOUND)

                for field, value in item.items():
                    if field != 'id':  # ID ni o‘zgartirmaymiz
                        setattr(obj, field, value)
                update_objs.append(obj)

            if update_objs:
                fields = [f for f in serializer.validated_data[0].keys() if f != 'id']
                model.objects.bulk_update(update_objs, fields=fields)

        return Response(self.get_serializer(update_objs, many=True).data, status=status.HTTP_200_OK)
