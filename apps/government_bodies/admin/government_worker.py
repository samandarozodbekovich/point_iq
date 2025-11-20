from django.contrib import admin

from apps.government_bodies.models import GovernmentWorker


@admin.register(GovernmentWorker)
class GovernmentWorkerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_uz', 'government__name_uz', 'position')
    search_fields = ('name_uz', 'government__name_uz', 'position')
    list_filter = ('government__name_uz', 'position')