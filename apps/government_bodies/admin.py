from django.contrib import admin

from apps.government_bodies.models import GovernmentBody


# Register your models here.

@admin.register(GovernmentBody)
class GovernmentBodyAdmin(admin.ModelAdmin):
    list_display = ['name_uz', 'address', 'longitude', 'latitude']
    list_filter = ['name_uz', 'address']
    search_fields = ['name_uz', 'address']

