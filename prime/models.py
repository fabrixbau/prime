from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils.timezone import now
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


class ActivityManager(models.Manager):
    def create_activity(self, user, name, description, days_of_week,start_time, duration_minutes, start_date, end_date):
        print(f"🚀 Creando actividad: {name}, días: {days_of_week}")
        
        if isinstance(days_of_week, str):  # Asegurar que no sea una cadena
            days_of_week = days_of_week.split(",")
        
        activity = self.create(
            user=user,
            name=name, 
            description=description,
            days_of_week=",".join(days_of_week),
            start_time = start_time,
            duration_minutes= duration_minutes,
            start_date = start_date,
            end_date = end_date
        )
        
        print(f"✅ Actividad creada: {activity}")
        
        activity.create_logs() #Method to generate automatically the logs
        return activity


DAYS_OF_WEEK_CHOICES = [
    ('Mon', 'Monday'),
    ('Tue', 'Tuesday'),
    ('Wed', 'Wednesday'),
    ('Thu', 'Thursday'),
    ('Fri', 'Friday'),
    ('Sat', 'Saturday'),
    ('Sun', 'Sunday'),
]

class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    days_of_week = models.CharField(max_length=21, help_text="Días separados por comas (ej: Mon,Tue,Wed)")
    start_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    #custom manager
    objects = ActivityManager()
    
    def get_days_list(self):
        """ Convierte la cadena en una lista de días """
        return self.days_of_week.split(",")
    
    def __str__(self):
        return self.name
    
    def create_logs(self):
        # Implementa la lógica para crear logs automáticamente
        start_date = self.start_date or now().date()
        end_date = self.end_date or start_date + timedelta(days=30)
        
        print(f"📆 Creando logs para {self.name} desde {start_date} hasta {end_date}")
        
        for single_date in date_range(start_date, end_date):
            day_abbr = single_date.strftime('%a')[:3]
            
            print(f"🔍 Verificando día: {single_date} ({day_abbr})")
            
            if day_abbr in self.get_days_list(): 
                log, created = ActivityLog.objects.get_or_create(activity=self, user=self.user, date=single_date)
                if created:
                    print(f"✅ Log creado para {single_date}")
                    
                
    def is_active_on_day(self, current_date):
        """Checks if the activity is active and scheduled for a specific day."""
        # Checks if the activity is on range of the dates
        if self.start_date and current_date < self.start_date:
            return False
        if self.end_date and current_date > self.end_date:
            return False
        
        # Checks if the activity is shceduled for the specific day
        day_abbr = current_date.strftime('%a')[:3]
        if day_abbr not in self.get_days_list():
            return False
        
        # Checks if exist exceptions for the day
        if ActivityExclusion.objects.filter(activity=self, date=current_date).exists():
            return False
        
        return True
    
    def create_logs_for_range(self, start_date, end_date):
        """
        Generate dinamics logs for a date range.
        """
        for single_date in date_range(start_date, end_date):
            day_abbr = single_date.strftime('%a')[:3]
            # Validate if the activity is programed for that day
            if day_abbr in self.get_days_list():
                # Create the log if dosen't exist yet
                ActivityLog.objects.get_or_create(activity=self, user=self.user, date=single_date)

    def update_activity(self, name, description, days_of_week, start_time, duration_minutes, start_date, end_date):
        self.name = name
        self.description = description
        self.days_of_week = ",".join(days_of_week)
        self.start_time = start_time
        self.duration_minutes = duration_minutes
        self.start_date = start_date
        self.end_date = end_date
        self.save()

        # Actualizar los logs asociados si cambian los días o las fechas
        self.update_logs()
    
        
    @property
    def end_time(self):
        """Calculates the time end based on the duration of the activity"""
        start_datetime = datetime.combine(datetime.today(), self.start_time)
        end_datetime = start_datetime + timedelta(minutes=self.duration_minutes)
        return end_datetime.time()

    def get_days_display(self):
        """Devuelve los días de la actividad en formato legible."""
        days = dict(DAYS_OF_WEEK_CHOICES)
        return ", ".join([days[day] for day in self.get_days_list() if day in days])
        
    def update_logs(self):
        # calculate the complete range of dates after update them
        start_date = self.start_date
        end_date = self.end_date
        
        valid_days = set(self.get_days_list())
        
        existing_logs = ActivityLog.objects.filter(activity=self)
        for log in existing_logs:
            log_day_abbr = log.date.strftime('%a')[:3]
            if log.date < start_date or log.date > end_date or log_day_abbr not in valid_days:
                log.delete()

        for single_date in date_range(start_date, end_date):
            day_abbr = single_date.strftime('%a')[:3]
            if day_abbr in valid_days:
                ActivityLog.objects.get_or_create(activity=self, user=self.user, date=single_date)

    
        for log in existing_logs:
            log_day_abbr = log.date.strftime('%a')[:3]
            if log.date < start_date or log.date > end_date or log_day_abbr not in valid_days:
                log.delete()
        
        # create new logs for the dates aditionals  
        for single_date in date_range(start_date, end_date):
            day_abbr = single_date.strftime('%a')[:3]
            if day_abbr in valid_days:
                ActivityLog.objects.get_or_create(activity=self, user=self.user, date=single_date)
            

    def calculate_metrics(self):
        logs = ActivityLog.objects.filter(activity=self)
        total_count = logs.count()
        completed_count = logs.filter(status='✔️').count()
        incompleted_count = total_count - completed_count
        return {
            'total_count': total_count,
            'completed_count':completed_count,
            'incompleted_count':incompleted_count,
            
        }

class ActivityLog(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('✔️', 'Completed'), ('❌', 'Missed')], null=True, blank=True)

    class Meta:
        unique_together = ('activity', 'user', 'date')  # Avoid the Owners

    def __str__(self):
        status_display = 'Completed' if self.status == '✔️' else 'Not Completed' if self.status == '❌' else 'Pending'
        return f"{self.activity.name} on {self.date} - {status_display}"

    @staticmethod
    def auto_mark_unmarked_activities():
        # Marca automáticamente como no completadas después de 24 horas
        unmarked_logs = ActivityLog.objects.filter(
            status__isnull=True,
            date__lt=timezone.now().date() - timedelta(days=1)
        )
        unmarked_logs.update(status='❌')

    @staticmethod
    def get_or_create_log(activity, user, target_date):
    # Search a log created or create a new if not exist
        log, created = ActivityLog.objects.get_or_create(
            activity = activity,
            user=user,
            date=target_date
        )
        if created:
            print(f"ActivityLog creado para {activity.name} el {target_date}")
        return log

class ActivityExclusion(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="exclusions")
    date = models.DateField()
    
    class Meta:
        unique_together = ('activity', 'date')

    def __str__(self):
        return f"Exclusion for {self.activity.name} on {self.date}"


@receiver(post_save, sender=Activity)
def create_activity_log(sender, instance, created, **kwargs):
    if created:
        today = timezone.now().date()
        
        # if doesn't have an end date, asumme it's an ongoing activity and create records for a one month 
        start_date = instance.start_date or today
        end_date = instance.end_date or start_date + timedelta(days=30)
        
        # validate days on the week
        if not instance.days_of_week:
            print(f"Error: Not defined days on the week {instance.name}")
            return
        
        # Crear logs para cada fecha en el rango, si coincide con los días seleccionados
        for single_date in date_range(start_date, end_date):
            # Aquí usamos la abreviatura de tres letras para verificar los días
            day_abbr = single_date.strftime('%a')[:3]
            if day_abbr in instance.get_days_list():
                ActivityLog.objects.get_or_create(
                    activity=instance,
                    user=instance.user,
                    date=single_date
                )
                print(f"Log creado para la fecha: {single_date}, actividad: {instance.name}")



