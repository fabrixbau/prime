from datetime import timedelta
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Activity, ActivityLog
from django import forms
from django.http import JsonResponse
from django.http import HttpResponseForbidden


# Vista principal


def home(request):
    user_profile = None
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)

    return render(request, 'prime/home.html', {'user_profile': user_profile})

# VISTA CALENDARIO


@login_required
def calendar_view(request):
    return render(request, 'prime/calendar_view.html')


@login_required
def get_events(request):
    logs = ActivityLog.objects.filter(activity__user=request.user)
    events = []
    for log in logs:
        events.append({
            'title': log.activity.name,
            'start': log.date.isoformat(),
            'color': 'green' if log.completed else 'red',
        })
    return JsonResponse(events, safe=False)

# Métricas de usuario


@login_required
def metrics(request):
    completed_activities = ActivityLog.objects.filter(
        activity__user=request.user, completed=True).count()
    missed_activities = ActivityLog.objects.filter(
        activity__user=request.user, completed=False, marked=True).count()
    context = {
        'completed_activities': completed_activities,
        'missed_activities': missed_activities,
    }
    return render(request, 'prime/metrics.html', context)

# Crear usuario


def crearUsuario(request):
    if request.method == "POST":
        dataUsuario = request.POST["nuevoUsuario"]
        dataPassword = request.POST["nuevoPassword"]
        dataEmail = request.POST["email"]

        nuevoUsuario = User.objects.create_user(
            username=dataUsuario, password=dataPassword, email=dataEmail
        )
        if nuevoUsuario:
            login(request, nuevoUsuario)
            return redirect("/complete-profile")

    return render(request, "prime/crear_usuario.html")

# Login de usuario


def loginUsuario(request):
    paginaDestino = request.GET.get("next", "/")
    context = {"destino": paginaDestino}

    if request.method == "POST":
        dataUsuario = request.POST["usuario"]
        dataPassword = request.POST["password"]
        dataDestino = request.POST.get("destino", "/")

        usuarioAuth = authenticate(
            request, username=dataUsuario, password=dataPassword
        )
        if usuarioAuth is not None:
            login(request, usuarioAuth)
            return redirect(dataDestino if dataDestino else "/")
        else:
            context = {"mensajeError": "Datos incorrectos"}

    return render(request, "prime/login.html", context)

# Logout de usuario


def logoutUsuario(request):
    logout(request)
    return redirect("/")

# Completar perfil de usuario


@login_required
def complete_profile(request):
    if request.method == "POST":
        request.user.last_name = request.POST["lastname"]
        request.user.save()

        user_profile, created = UserProfile.objects.get_or_create(
            user=request.user
        )
        user_profile.nickname = request.POST["nickname"]
        user_profile.age = request.POST["age"]
        user_profile.save()

        return redirect("/")

    return render(request, "prime/complete_profile.html")

# Formulario para crear o editar actividades


DAYS_OF_WEEK = [
    ('Mon', 'Monday'),
    ('Tue', 'Tuesday'),
    ('Wed', 'Wednesday'),
    ('Thu', 'Thursday'),
    ('Fri', 'Friday'),
    ('Sat', 'Saturday'),
    ('Sun', 'Sunday'),
]


class ActivityForm(forms.ModelForm):
    days_of_week = forms.MultipleChoiceField(
        choices=DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Activity
        fields = ['name', 'description', 'days_of_week',
                  'start_time', 'duration_minutes']


@login_required
def activity_list(request):
    activities = Activity.objects.filter(
        user=request.user).order_by('start_time')

    days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    today = timezone.now().date()
    activities_by_day = []

    for i, day in enumerate(days_of_week):
        day_activities = []
        date_of_day = today + timedelta(days=(i - today.weekday()) % 7)
        for activity in activities:
            logs = activity.activitylog_set.filter(date=date_of_day)

            if logs.exists():
                day_activities.append((activity, logs))

        activities_by_day.append(
            (f"{day} - {date_of_day.strftime('%d %B')}", day_activities))

    return render(request, 'prime/activity_list.html', {
        'activities_by_day': activities_by_day,
    })


# Crear actividad


@login_required
def create_activity(request):
    if request.method == 'POST':
        print(request.POST)  # Add this line to print the incoming POST data
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.user = request.user
            activity.days_of_week = " ".join(
                request.POST.getlist('days_of_week'))
            activity.save()
            return redirect('prime:activity_list')
        else:
            print(form.errors)  # Print form errors if the form is invalid
    else:
        form = ActivityForm()
    return render(request, 'prime/activity_form.html', {'form': form})

# Editar actividad


@login_required
def edit_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id, user=request.user)
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            return redirect('prime:activity_list')
    else:
        form = ActivityForm(instance=activity)

    return render(request, 'prime/activity_form.html', {'form': form})

# Detalles de la actividad


@login_required
def activity_detail(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id, user=request.user)
    return render(request, 'prime/activity_detail.html',
                  {'activity': activity})

# Marcar actividad como completada/no completada


@login_required
def mark_activity(request, log_id):
    log = get_object_or_404(ActivityLog, id=log_id,
                            activity__user=request.user)

    completed = request.GET.get('completed')

    if completed is not None:
        log.completed = completed.lower() == 'true'
        log.marked = True
        log.save()
        return redirect('prime:activity_list')

    return render(request, 'prime/mark_activity.html', {'log': log})

# Eliminar actividad


@login_required
def delete_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id, user=request.user)

    if request.method == "POST":
        activity.delete()
        return redirect('prime:activity_list')

    return render(request, 'prime/delete_activity_confirm.html',
                  {'activity': activity})

# LOGS


@receiver(post_save, sender=Activity)
def create_activity_log(sender, instance, created, **kwargs):
    if created:
        today = timezone.now().date()
        days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        # Loop through the next 52 weeks (1 year)
        for week in range(52):
            week_start = today + timedelta(weeks=week)
            for day in instance.days_of_week.split():
                day_number = days_of_week.index(day)

                # Calculate the exact date for the current day of the week
                date_for_log = week_start + \
                    timedelta(days=(day_number - week_start.weekday()) % 7)

                # Check if log already exists for this date
                if not ActivityLog.objects.filter(activity=instance,
                                                  date=date_for_log).exists():
                    ActivityLog.objects.create(
                        activity=instance, date=date_for_log
                    )


@login_required
def delete_activity_log(request, log_id):
    log = get_object_or_404(ActivityLog, id=log_id,
                            activity__user=request.user)

    if request.method == "POST":
        log.delete()
        return redirect('prime:activity_list')

    return HttpResponseForbidden("Cannot delete this activity log.")
