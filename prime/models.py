from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Activity(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    days_of_week = models.CharField(max_length=27)  # e.g., 'MTWTFSS'
    duration_minutes = models.PositiveIntegerField()  # Duration in minutes
    start_time = models.TimeField()  # Scheduled start time
    end_time = models.TimeField(null=True, blank=True)  # Actual end time
    # Indicates if the activity is currently active
    active = models.BooleanField(default=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)  # Relates to the user

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
        return ", ".join([days[day] for day in self.days_of_week.split()
                          if day in days])

    def is_active_today(self):
        # Returns True if the activity is scheduled for today
        import datetime
        today = datetime.datetime.today().strftime(
            '%A')[0]  # First letter of today's day
        return today in self.days_of_week


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10)
    lastname = models.CharField(max_length=50, blank=True)
    nickname = models.CharField(max_length=50, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.username


class ActivityLog(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        status = 'Completed' if self.completed else 'Not Completed'
        return f"{self.activity.name} on {self.date} - {status}"
