from django.db import models

# Create your models here.
class BaseTimeModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseNameModel(models.Model):
    name_uz = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100, null=True, blank=True)
    name_uz_cyr = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        abstract = True