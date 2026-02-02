from django.contrib import admin

from apps.citizens.people_education.models import PeopleEducation


@admin.register(PeopleEducation)
class PeopleEducationAdmin(admin.ModelAdmin):
    list_display = ('id','district__name_uz', 'regional_school', 'regional_kindergarten')
    list_filter = ('district__name_uz','regional_school', 'regional_kindergarten')
    search_fields = ('district__name_uz',)
