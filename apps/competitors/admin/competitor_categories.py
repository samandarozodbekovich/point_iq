from django.contrib import admin

from apps.competitors.competitor_categories.models import CompetitorCategory



@admin.register(CompetitorCategory)
class CompetitorCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'name_ru', 'name_cyr', 'external_id')
    list_filter = ('name_uz', 'name_ru', 'name_cyr')
    ordering = ('-created_at',)

