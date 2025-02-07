from __future__ import absolute_import, unicode_literals

# Importa la aplicación Celery para que esté disponible como makeprime.celery
from .celery import app as celery_app

__all__ = ('celery_app',)
