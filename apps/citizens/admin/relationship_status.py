from django.contrib import admin

from apps.citizens.relationship_status.models import RelationshipStatus


@admin.register(RelationshipStatus)
class RelationshipStatusAdmin(admin.ModelAdmin):
    list_display = ('name_uz',)
    list_filter = ('name_uz',)
    list_per_page = 50