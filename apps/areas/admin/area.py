from django.contrib import admin

from apps.areas.areas.models import Area

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('id','name_uz','district')
    search_fields = ('name_uz',)
    list_filter = ('district',)