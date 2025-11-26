from django.db.models import Avg, Count
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.competitors.competitor_review.models import CompetitorReview

@receiver([post_delete, post_save], sender=CompetitorReview)
def update_competitor_rating(sender, instance, **kwargs):
    competitor = instance.competitor
    agg = competitor.reviews.aggregate(
        average_rating=Avg('rating'),
        review_count=Count('id')
    )
    avg_rating = agg['average_rating']
    competitor.average_rating = round(avg_rating, 2) if avg_rating is not None else None
    competitor.save(update_fields=['average_rating', 'review_count'])


