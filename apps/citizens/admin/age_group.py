from django.contrib import admin

from apps.citizens.age_groups.models import AgeGroup


@admin.register(AgeGroup)
class AgeGroupAdmin(admin.ModelAdmin):
    list_display = ('name_uz',)
    list_per_page = 50