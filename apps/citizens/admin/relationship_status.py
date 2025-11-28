from django.contrib import admin

from apps.citizens.relationship_status.models import RelationshipStatus, RelationshipStatusPopulation


@admin.register(RelationshipStatus)
class RelationshipStatusAdmin(admin.ModelAdmin):
    list_display = ('id','name_uz','name_ru', 'name_cyr')
    list_filter = ('name_uz','name_ru','name_cyr')
    list_per_page = 50



@admin.register(RelationshipStatusPopulation)
class RelationshipStatusPopulationAdmin(admin.ModelAdmin):
    list_display = ('population','relationship_status', 'count')
    list_filter = ('population','relationship_status')
