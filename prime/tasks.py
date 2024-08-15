from celery import shared_task
from .models import ActivityLog


@shared_task
def auto_mark_unmarked_activities():
    ActivityLog.auto_mark_unmarked_activities()
