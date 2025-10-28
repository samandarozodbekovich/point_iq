from django.contrib import admin

from apps.citizens.religion_counts.models import ReligionCount


@admin.register(ReligionCount)
class ReligionCountAdmin(admin.ModelAdmin):
    list_display = ('population', 'religion', 'count')
    list_filter = ('population',)
    list_per_page = 50