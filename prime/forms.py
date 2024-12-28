from django import forms
from .models import Activity

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = [
            'name', 'description', 'days_of_week', 'start_time', 'duration_minutes', 'start_date', 'end_date'
        ]
        widgets = {
            'days_of_week': forms.CheckboxSelectMultiple(
                choices=[
                    ('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'),
                    ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')
                ]
            ),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type':'date'}),
            'start_time': forms.TimeInput(attrs={'type':'time'}),
        }