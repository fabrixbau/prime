from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Configuración del entorno Django para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'makeprime.settings')

app = Celery('makeprime')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'auto-mark-unmarked-activities-every-day': {
        'task': 'prime.tasks.auto_mark_unmarked_activities',
        # Se ejecuta a la medianoche todos los días
        'schedule': crontab(hour=0, minute=0),
    },
}
