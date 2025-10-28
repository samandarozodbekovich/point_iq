from django.contrib import admin

from apps.citizens.ethnicities.models import Ethnicity


@admin.register(Ethnicity)
class EthnicityAdmin(admin.ModelAdmin):
    list_display = ('name_uz',)
    list_per_page = 50