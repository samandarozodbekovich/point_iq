from django.contrib import admin

from apps.citizens.population.models import Citizen
from apps.citizens.age_counts.models import PopulationStatistic
from apps.citizens.age_groups.models import AgeGroup
from apps.citizens.ethnicities.models import Ethnicity
from apps.citizens.ethnicity_count.models import EthnicityCount
from apps.citizens.relationship_status.models import RelationshipStatus
from apps.citizens.relationship_counts.models import RelationshipCount
from apps.citizens.religions.models import Religion
from apps.citizens.religion_counts.models import ReligionCount


class CitizenAdmin(admin.ModelAdmin):
    list_display = ('apartment', 'count_male', 'count_female', 'average_income', 'unemployment_rate')
    search_fields = ('apartment',)
    list_filter = ('apartment',)
    list_per_page = 50


class PopulationAdmin(admin.ModelAdmin):
    list_display = ('population', 'age_group','population_count')
    list_filter = ('population',)
    list_per_page = 50


class AgeGroupAdmin(admin.ModelAdmin):
    list_display = ('name_uz',)
    list_per_page = 50


class EthnicityAdmin(admin.ModelAdmin):
    list_display = ('name_uz',)
    list_per_page = 50


class EthnicityCountAdmin(admin.ModelAdmin):
    list_display = ('population','ethnicity', 'count')
    list_filter = ('ethnicity',)
    list_per_page = 50


class RelationshipCountAdmin(admin.ModelAdmin):
    list_display = ('population', 'relationship_status', 'count')
    list_filter = ('population','relationship_status')
    list_per_page = 50


class RelationshipStatusAdmin(admin.ModelAdmin):
    list_display = ('name_uz',)
    list_filter = ('name_uz',)
    list_per_page = 50


class ReligionAdmin(admin.ModelAdmin):
    list_display = ('name_uz',)
    list_filter = ('name_uz',)


class ReligionCountAdmin(admin.ModelAdmin):
    list_display = ('population', 'religion', 'count')
    list_filter = ('population',)
    list_per_page = 50


admin.site.register(Citizen, CitizenAdmin)
admin.site.register(PopulationStatistic, PopulationAdmin)
admin.site.register(Ethnicity, EthnicityAdmin)
admin.site.register(EthnicityCount, EthnicityCountAdmin)
admin.site.register(RelationshipCount, RelationshipCountAdmin)
admin.site.register(RelationshipStatus, RelationshipStatusAdmin)
admin.site.register(Religion, ReligionAdmin)
admin.site.register(ReligionCount, ReligionCountAdmin)
admin.site.register(AgeGroup, AgeGroupAdmin)




