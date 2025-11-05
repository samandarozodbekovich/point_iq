from django.contrib import admin

from apps.citizens.religions.models import Religion, ReligionCount


@admin.register(Religion)
class ReligionAdmin(admin.ModelAdmin):
    list_display = ('name_uz',)
    list_filter = ('name_uz',)


@admin.register(ReligionCount)
class ReligionCountAdmin(admin.ModelAdmin):
    list_display = ('population','religion', 'count')
    list_filter = ('population','religion')