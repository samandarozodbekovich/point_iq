from django.contrib import admin

from apps.citizens.religions.models import Religion


@admin.register(Religion)
class ReligionAdmin(admin.ModelAdmin):
    list_display = ('name_uz',)
    list_filter = ('name_uz',)