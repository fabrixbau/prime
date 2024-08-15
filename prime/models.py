from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import post_save


# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10)
    lastname = models.CharField(max_length=50, blank=True)
    nickname = models.CharField(max_length=50, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.username


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    days_of_week = models.CharField(max_length=50)
    start_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} ({self.get_days_display()})"

    def get_days_display(self):
        days = {
            'Mon': 'Monday',
            'Tue': 'Tuesday',
            'Wed': 'Wednesday',
            'Thu': 'Thursday',
            'Fri': 'Friday',
            'Sat': 'Saturday',
            'Sun': 'Sunday'
        }
        return ", ".join(
            [days[day] for day in self.days_of_week.split() if day in days])

    @property
    def end_time(self):
        start_datetime = datetime.combine(datetime.today(), self.start_time)
        end_datetime = start_datetime + \
            timedelta(minutes=self.duration_minutes)
        return end_datetime.time()


class ActivityLog(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    date = models.DateField()  # Día específico de la actividad
    completed = models.BooleanField(default=False)
    marked = models.BooleanField(default=False)

    def __str__(self):
        status = 'Completed' if self.completed else 'Not Completed'
        return f"{self.activity.name} on {self.date} - {status}"

    @staticmethod
    def auto_mark_unmarked_activities():
        # Marca automáticamente como no completadas después de 24 horas
        unmarked_logs = ActivityLog.objects.filter(
            marked=False,
            date__lt=timezone.now().date() - timedelta(days=1)
        )
        for log in unmarked_logs:
            log.completed = False
            log.marked = True
            log.save()


@receiver(post_save, sender=Activity)
def create_activity_log(sender, instance, created, **kwargs):
    if created:
        # Crear un ActivityLog para cada día de la semana seleccionado
        for day in instance.days_of_week.split():
            day_number = ['Mon', 'Tue', 'Wed', 'Thu',
                          'Fri', 'Sat', 'Sun'].index(day)
            today = timezone.now().date()
            days_ahead = (day_number - today.weekday() + 7) % 7
            next_occurrence = today + timedelta(days=days_ahead)
            ActivityLog.objects.create(activity=instance, date=next_occurrence)
