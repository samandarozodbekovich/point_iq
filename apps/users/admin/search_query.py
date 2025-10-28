from django.contrib import admin

from apps.users.models.search_query import SearchQuery


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_query', 'radius_miles', 'latitude', 'longitude',]
    search_fields = ['user', 'user_query', 'radius_miles']
    list_filter = ['user', 'user_query', 'radius_miles']
    ordering = ('user', 'user_query', '-created_at')
    readonly_fields = ('created_at', 'updated_at')

