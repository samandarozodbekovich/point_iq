from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'get_place.settings')
app = Celery('get_place')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# This task works at 00:00 am in every day
# app.conf.beat_schedule = {
#     'daily-user-count': {
#         'task': 'apps.users.tasks.daily_user_count',
#         'schedule': crontab(hour=0, minute=0),  #at 00:00 am every day
#     },
# }
