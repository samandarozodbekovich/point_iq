from django.contrib import admin

from apps.citizens.ethnicity_count.models import EthnicityCount


@admin.register(EthnicityCount)
class EthnicityCountAdmin(admin.ModelAdmin):
    list_display = ('population','ethnicity', 'count')
    list_filter = ('ethnicity',)
    list_per_page = 50