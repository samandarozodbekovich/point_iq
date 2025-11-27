from django.contrib import admin

from apps.citizens.people_consume.models import PeopleConsume


@admin.register(PeopleConsume)
class PeopleConsumeAdmin(admin.ModelAdmin):
    list_display = ('id','district__name_uz', 'month', 'year')
    search_fields = ('district__name_uz', 'month', 'year')
    list_filter = ('district__name_uz', 'month', 'year')
