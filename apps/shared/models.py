from django.db import models

# Create your models here.
class BaseTimeModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def soft_delete(self, user=None):
        self.is_deleted = True
        self.save()

    # Restore
    def restore(self):
        self.is_deleted = False
        self.save()

    # Delete permanently
    def hard_delete(self):
        super().delete()


class BaseNameModel(models.Model):
    name_uz = models.CharField(max_length=100, null=True, blank=True)
    name_ru = models.CharField(max_length=100, null=True, blank=True)
    name_cyr = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """Manager that hides soft-deleted rows."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)