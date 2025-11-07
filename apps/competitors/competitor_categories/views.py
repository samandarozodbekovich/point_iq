# populate_categories.py
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import CompetitorCategory
from .serializers import CompetitorCategorySerializer



class CompetitorCategoryViewSet(viewsets.ModelViewSet):
    """
    CompetitorCategory uchun ViewSet.
    Oddiy CRUD imkoniyatlari mavjud.
    """
    queryset = CompetitorCategory.objects.all()
    serializer_class = CompetitorCategorySerializer

    # GET requestda kerak bo'lsa til tanlash imkoniyati
    def list(self, request, *args, **kwargs):
        lang = request.GET.get('lang', 'uz')
        queryset = self.get_queryset()
        data = []
        for category in queryset:
            data.append({
                'id': category.id,
                'name': getattr(category, f'name_{lang}', category.name_uz),
                'external_id': category.external_id
            })
        return Response(data, status=status.HTTP_200_OK)

    # create va update metodlar ModelViewSet orqali avtomatik ishlaydi
    # agar qo'shimcha validatsiya yoki logikani yozmoqchi bo'lsangiz, create() va update() override qilishingiz mumkin
