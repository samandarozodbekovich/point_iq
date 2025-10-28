from django.contrib import admin

from apps.citizens.relationship_counts.models import RelationshipCount


@admin.register(RelationshipCount)
class RelationshipCountAdmin(admin.ModelAdmin):
    list_display = ('population', 'relationship_status', 'count')
    list_filter = ('population','relationship_status')
    list_per_page = 50