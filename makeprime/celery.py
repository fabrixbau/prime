# prime/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Establece el módulo de configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'makeprime.settings')

# Crea una instancia de Celery
app = Celery('makeprime')

# Lee la configuración desde settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descubre tareas automáticamente
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
