from datetime import timezone

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from apps.competitors.competitor_categories.models import CompetitorCategory
from apps.areas.places.models import Place
from apps.shared.models import BaseNameModel, BaseTimeModel
from apps.users.models import User


# class SoftDeleteManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(deleted_at__isnull=True)
#
#
# class AllObjectsManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset()


class Competitor(BaseNameModel, BaseTimeModel):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(CompetitorCategory, on_delete=models.CASCADE)
    address = models.CharField(max_length=120)
    longitude = models.FloatField()
    latitude = models.FloatField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    ,null=True,blank=True)

    # owner = models.ForeignKey(User, on_delete=models.CASCADE)
    # deleted_at = models.DateTimeField(null=True, blank=True)
    # deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deleted_competitors')
    #
    # def soft_delete(self, user=owner):
    #     self.deleted_at = timezone.now()
    #     self.deleted_by = user
    #     self.save(update_fields=['deleted_at', 'deleted_by'])
    #
    # def restore(self):
    #     self.deleted_at = None
    #     self.deleted_by = None
    #     self.save(update_fields=['deleted_at', 'deleted_by'])
    #
    # def hard_delete(self):
    #     super().delete()
    #
    # def __str__(self):
    #     return f"{self.name_uz} at {self.place}"

