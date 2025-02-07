from datetime import  timedelta, date, datetime
from django.utils import timezone
from django.utils.timezone import now
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from prime.forms import ActivityForm
from .models import UserProfile, Activity, ActivityLog, ActivityExclusion
from django import forms
from django.http import JsonResponse
from django.http import HttpResponseForbidden
from .utils import date_range
from calendar import monthrange, monthcalendar



"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""
"""XXXXXXXXXXXX                                                      USUARIOS                                                    XXXXXXXXXXX"""
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""

# Vista principal para logearse y que redirija ella django
def home(request):
    user_profile = None
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)

    return render(request, 'prime/home.html', {'user_profile': user_profile})

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
# Métricas de usuario
@login_required



# Vista principal


def home(request):
    user_profile = None
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)

    return render(request, 'prime/home.html', {'user_profile': user_profile})



"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""
"""XXXXXXXXXXXX                                                       ACTIVITIES                                                  XXXXXXXXXXX"""
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""

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


# CREATE ACTIVITY
@login_required
def create_activity(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        days_of_week = request.POST.getlist('days_of_week') or []
        valid_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        if not all(day in valid_days for day in days_of_week):
            return render(request, 'prime/new_activity.html', {'error': 'Días inválidos seleccionados.'})
        
        start_time = request.POST.get('start_time', '').strip()
        duration_minutes = request.POST.get('duration_minutes', '').strip()
        
        # Maneja start_date y end_date
        start_date = request.POST.get('start_date') or now().date()
        end_date = request.POST.get('end_date') or None

        # Crear y guardar la instancia de Activity con el usuario asignado
        activity = Activity.objects.create_activity(
            user=request.user,
            name=name,
            description=description,
            days_of_week=days_of_week,
            start_time=start_time,
            duration_minutes=duration_minutes,
            start_date=start_date,
            end_date=end_date
        )
        
        return redirect('prime:activity_list')

    return render(request, 'prime/new_activity.html')



"""
TODO: PREGUNTAR A CHAT COMO LE PODRIA HACER SI QUIERO EDITAR LA ACTIVIDAD, YA SABES HABLAMOS DE PATCH IGUAL PREGUNTAR SI CONVIENE PATCH O PUT
"""
# # Editar actividad 
@login_required
def edit_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id, user=request.user)
    
    days_of_week_choices = {
    'Mon': 'Monday',
    'Tue': 'Tuesday',
    'Wed': 'Wednesday',
    'Thu': 'Thursday',
    'Fri': 'Friday',
    'Sat': 'Saturday',
    'Sun': 'Sunday',
    }
    
    if request.method == 'GET':
        return render(request, 'prime/edit_activity.html', {'activity': activity, 'days_of_week_choices': days_of_week_choices})
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description','').strip()
        days_of_week = request.POST.getlist('days_of_week') or []
        start_time = request.POST.get('start_time', '').strip()
        duration_minutes = request.POST.get('duration_minutes','').strip()
        start_date = request.POST.get('start_date') or activity.start_date
        end_date = request.POST.get('end_date') or activity.end_date
        
        activity.update_activity(
            name=name,
            description = description,
            days_of_week = days_of_week,
            start_time = start_time,
            duration_minutes = duration_minutes,
            start_date = start_date,
            end_date = end_date
        )
        
        return redirect('prime:activity_list')
    
    return render(request, 'prime/edit_activity.html', {'activity': activity})
    
# DELETE ACTIVITY

@login_required
def delete_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id, user=request.user)

    if request.method == "POST":
        activity.delete()
        return redirect('prime:activity_list')

    return render(request, 'prime/delete_activity_confirm.html',
                  {'activity': activity})
    
    
# DELETE ACTIVITY LOG FOR A DAY
@login_required
def delete_activity_for_day(request, activity_id, date):
    activity = get_object_or_404(Activity, id=activity_id, user=request.user)
    try:
        day = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponseForbidden("Date invalid. Use the format YYYY-MM-DD.")

    ActivityExclusion.objects.get_or_create(activity=activity, date=day)
    ActivityLog.objects.filter(activity=activity, date=day).delete()

    return redirect('prime:activity_list')


# Delete all the actitivities

@login_required
def delete_all_activities(request):
    Activity.objects.filter(user=request.user).delete()
    return redirect('prime:activity_list')


# Detalles de la actividad
"""
TODO: REVISAR QUE DETALLES QUIERO OBTENER DE LA ACTIVIDAD
"""
@login_required
def activity_detail(request, activity_id):
    # get the activity, ensuring that it belongs to the current user
    activity = get_object_or_404(Activity, id=activity_id, user=request.user)
    
    # if is a request AJAX, return data JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            "id": activity.id,
            "name": activity.name,
            "description": activity.description,
            "days_of_week": activity.get_days_list(), 
            "start_time": activity.start_time.strftime('%H:%M'),
            "duration_minutes": activity.duration_minutes,
            "start_date": activity.start_date.strftime('%Y-%m-%d') if activity.start_date else None,
            "end_date": activity.end_date.strftime('%Y-%m-%d') if activity.end_date else None,            
        })
    
    # if dosen't is AJAX, render normal template
    return render(request, 'prime/activity_detail.html', {'activity': activity})


"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""
"""XXXXXXXXXXXX                                                       VIEW ACTIVITIES                                             XXXXXXXXXXX"""
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""
@login_required
def activity_list(request):
    # Obtener el año y mes de la solicitud o usar los valores actuales
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))

    # Rango de fechas visibles en el calendario
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])

    # Filtrar actividades del usuario actual
    activities = Activity.objects.filter(user=request.user)

    # Generar logs dinámicos para todas las actividades dentro del rango visible
    for activity in activities:
        activity.create_logs_for_range(first_day, last_day)

    # Crear la estructura de datos del calendario
    calendar_data = []
    for week in monthcalendar(year, month):
        week_data = []
        for day in week:
            if day == 0:  # Día vacío en el calendario
                week_data.append({"date": None, "activities": []})
                continue  # Saltar al siguiente día en el bucle

            # Día válido: generar current_date
            current_date = date(year, month, day)
            day_activities = []

            # Procesar actividades para este día
            for activity in activities:
                if activity.is_active_on_day(current_date):
                    # Excluir días marcados como excluidos
                    if not ActivityExclusion.objects.filter(activity=activity, date=current_date).exists():
                        log = ActivityLog.objects.filter(activity=activity, date=current_date).first()
                        day_activities.append((activity, log.status if log else None, log))

            # Agregar datos del día al calendario
            week_data.append({"date": current_date, "activities": day_activities})

        calendar_data.append(week_data)

    # Calcular los meses anterior y siguiente
    previous_month = (month - 1) if month > 1 else 12
    previous_year = year if month > 1 else year - 1
    next_month = (month + 1) if month < 12 else 1
    next_year = year if month < 12 else year + 1

    return render(request, 'prime/activity_list.html', {
        'calendar_data': calendar_data,
        'month': month,
        'year': year,
        'previous_month': {'month': previous_month, 'year': previous_year},
        'next_month': {'month': next_month, 'year': next_year},
    })



# Mark activity as completed or incompleted

@login_required
def mark_activity(request, log_id):
    if request.method == 'POST':        
        log = get_object_or_404(ActivityLog, id=log_id, user=request.user)
        status = request.POST.get("status")
     
        if status not in ['✔️', '❌']:
                return HttpResponseForbidden("Invalidated state.")

        # Actualizar el estado del registro
        log.status = status
        log.save()
        
        return redirect('prime:activity_list')
        


# LOGS

# @login_required
# def delete_activity_log(request, log_id):
#     log = get_object_or_404(ActivityLog, id=log_id, user=request.user)

#     if request.method == "POST"
#         print(f"Eliminando registro de ActivityLog con ID: {log_id}")
#         log.delete()
#         return redirect('prime:activity_list')

#     return HttpResponseForbidden("Cannot delete this activity log.")
@login_required
def delete_activity_for_day(request, activity_id, date):
    activity = get_object_or_404(Activity, id=activity_id, user=request.user)
    try:
        day = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponseForbidden("Date invalid. Use the format YYYY-MM-DD.")

    # Crea la exclusión para ese día
    exclusion, created = ActivityExclusion.objects.get_or_create(activity=activity, date=day)

    # Elimina el log asociado
    ActivityLog.objects.filter(activity=activity, date=day).delete()

    return redirect('prime:activity_list')



"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""
"""XXXXXXXXXXXX                                                       METRICAS                                                    XXXXXXXXXXX"""
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""
# Métricas de usuario
@login_required
def metrics(request):
    # get all activitys from user
    activities = Activity.objects.filter(user=request.user)
    
    # make dictionary to store all activity data
    activity_stats = []
    
    for activity in activities:
        # range of dates
        metrics = activity.calculate_metrics()
        activity_stats.append({
            'name': activity.name,
            **metrics
        })
        
    context = {'activity_stats': activity_stats}
    return render(request, 'prime/metrics.html', context)

        

