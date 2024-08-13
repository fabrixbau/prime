from django.contrib import admin
from .models import Activity, UserProfile


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'days_of_week',
                    'duration_minutes', 'start_time', 'user')
    list_filter = ('user', 'days_of_week')
    search_fields = ('name', 'description', 'user__username')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname', 'age', 'phone_number')
    search_fields = ('user__username', 'nickname')
