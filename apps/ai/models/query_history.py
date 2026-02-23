from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class QueryHistory(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='query_histories'
    )
    user_query = models.TextField(db_index=True)
    business_type = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    response_json = models.JSONField(default=dict, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='processing'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_query} ({self.status})"