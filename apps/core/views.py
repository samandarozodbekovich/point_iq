from rest_framework.decorators import action
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status

class BaseBulkMethods:
    lang_fields = ['_uz', '_ru', '_uz_cyr']  # suffixlarni '_' bilan aniqlash, Django field nomlariga mos

    def get_lang_data(self, item):
        """
        Har bir tildagi ma'lumotni ajratish (agar kerak bo‘lsa)
        """
        # Bu funksiya oldin redundant edi, endi oddiy qilib
        return [item]  # har bir obyektni listga o‘rab beradi, bulk_create uchun yetarli

    @action(detail=False, methods=['post'], url_path='create')
    def bulk_create(self, request, *args, **kwargs):
        """
        POST /model/create/
        Bir nechta obyektlarni bitta request orqali yaratish
        """
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        model = self.get_queryset().model

        all_objects = []
        with transaction.atomic():
            for item in serializer.validated_data:
                for li in self.get_lang_data(item):
                    all_objects.append(model(**li))
            if all_objects:
                model.objects.bulk_create(all_objects, ignore_conflicts=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['put', 'patch'], url_path='update')
    def bulk_update(self, request, *args, **kwargs):
        """
        PUT /model/update/
        Bir nechta obyektlarni bitta request orqali yangilash
        """
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

        return Response(serializer.data, status=status.HTTP_200_OK)
