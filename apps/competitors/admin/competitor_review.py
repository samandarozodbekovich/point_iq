from django.contrib import admin

from apps.competitors.competitor_review.models import CompetitorReview


class CompetitorReviewInline(admin.TabularInline):
    model = CompetitorReview
    extra = 1


@admin.register(CompetitorReview)
class CompetitorReviewAdmin(admin.ModelAdmin):
    list_display = ('competitor', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment', 'user__phone_number', 'competitor__name_uz')