from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date
from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import post_save
from .utils import date_range



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
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    days_of_week = models.CharField(max_length=50)
    start_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True,blank=True)

    def is_within_date_range(self, current_date):
        """cheks if activity is within the date range"""
        # Si no hay fecha de inicio, se considera continuo
        if not self.start_date:
            return True
        # Si hay fecha de inicio, verifica que esté dentro del rango
        if self.start_date and current_date < self.start_date:
            return False
        if self.end_date and current_date > self.end_date:
            return False
        return True
        
    def is_scheduled_for_day(self, current_date):
        day_abbr = current_date.strftime('%a')[:3]
        print(f"Verificando si {self.name} está programada para {current_date} ({day_abbr}). Días: {self.days_of_week}")
        result = day_abbr in self.days_of_week.split()
        print(f"Resultado: {result}")
        return result

    


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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()  # Día específico de la actividad
    status = models.CharField(max_length=10, choices=[('✔️', 'Completed'), ('❌', 'Missed')], null=True, blank=True)

    def __str__(self):
        status_display = 'Completed' if self.status == '✔️' else 'Not Completed' if self.status == '❌' else 'Pending'
        return f"{self.activity.name} on {self.date} - {status_display}"

    @staticmethod
    def auto_mark_unmarked_activities():
        # Marca automáticamente como no completadas después de 24 horas
        unmarked_logs = ActivityLog.objects.filter(
            status__isnull=True,
            date__lt=timezone.now().date() -timedelta(days=1)
        )
        for log in unmarked_logs:
            log.status = '❌'
            log.save()
            
    @staticmethod
    def get_or_create_log(activity, user, target_date):
    # Search a log created or create if not exist
        log, created = ActivityLog.objects.get_or_create(
            activity = activity,
            user=user,
            date=target_date
        )
        if created:
            print(f"ActivityLog creado para {activity.name} el {target_date}")
        return log


""" 
* Function to create automaticly logs of activity each time is created an model of Activity
""" 
@receiver(post_save, sender=Activity)
def create_activity_log(sender, instance, created, **kwargs):
    if created:
        today = timezone.now().date()
        
        if instance.user is None:
            raise ValueError("The activitiy must have a user asigned to create logs.")
        
        # if doesn't have an end date, asumme it's an ogoing activity and create records for a one month 
        start_date = instance.start_date or timezone.now().date()
        end_date = instance.end_date or start_date + timedelta(days=30)
        print(f"Rango de fechas: {start_date} - {end_date}")
        
        # Depuración de fechas generadas
        print(f"Fechas generadas por date_range: {list(date_range(start_date, end_date))}")
        
        # Validación adicional para días de la semana vacíos
        if not instance.days_of_week:
            print(f"Error: No se definieron días de la semana para {instance.name}")
            return
        
        for single_date in date_range(start_date, end_date):
            # Aquí usamos la abreviatura de tres letras para verificar los días
            day_abbr = single_date.strftime('%a')[:3]
            if day_abbr in instance.days_of_week.split():
                ActivityLog.objects.get_or_create(
                    activity=instance,
                    user=instance.user,
                    date=single_date
                )
                print(f"Creando log para fecha: {single_date}, actividad: {instance.name}")



