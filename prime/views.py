from datetime import  timedelta, date, datetime
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
from .utils import date_range
from calendar import monthrange



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

# VISTA CALENDARIO


"""
TODO: CREATE VIEW OF CALENDAR AND LOGIC DEVELOPMENT









"""

@login_required
def calendar_view(request):
    return render(request, 'prime/calendar_view.html')


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
        print(f"Días de la semana enviados por el formulario: {request.POST.getlist('days_of_week')}")
        days_of_week = ' '.join(request.POST.getlist('days_of_week'))
        if not days_of_week:
            print("Error: No se seleccionaron días de la semana.")
            return render(request, 'prime/new_activity.html', {'error': 'Debes seleccionar al menos un día de la semana.'})
        
        start_time = request.POST.get('start_time', '').strip()
        duration_minutes = request.POST.get('duration_minutes', '').strip()
        
        # Maneja start_date y end_date
        start_date = request.POST.get('start_date')
        start_date = start_date or timezone.now().date()
        end_date = request.POST.get('end_date') or None

        # Crear y guardar la instancia de Activity con el usuario asignado
        activity = Activity(
            user=request.user,
            name=name,
            description=description,
            days_of_week=days_of_week,
            start_time=start_time,
            duration_minutes=duration_minutes,
            start_date=start_date,
            end_date=end_date
        )
        activity.save()  # Esto activará el receiver que creará los ActivityLog

        return redirect('prime:activity_list')

    return render(request, 'prime/new_activity.html')



"""
TODO: PREGUNTAR A CHAT COMO LE PODRIA HACER SI QUIERO EDITAR LA ACTIVIDAD, YA SABES HABLAMOS DE PATCH IGUAL PREGUNTAR SI CONVIENE PATCH O PUT
"""
# # Editar actividad 

# @login_required
# def edit_activity(request, activity_id):
#     activity = get_object_or_404(Activity, id=activity_id, user=request.user)
#     if request.method == 'POST':
#         form = ActivityForm(request.POST, instance=activity)
#         if form.is_valid():
#             form.save()
#             return redirect('prime:activity_list')
#     else:
#         form = ActivityForm(instance=activity)

#     return render(request, 'prime/activity_form.html', {'form': form})

# DELETE ACTIVITY

@login_required
def delete_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id, user=request.user)

    if request.method == "POST":
        activity.delete()
        return redirect('prime:activity_list')

    return render(request, 'prime/delete_activity_confirm.html',
                  {'activity': activity})

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
    activity = get_object_or_404(Activity, id=activity_id, user=request.user)
    return render(request, 'prime/activity_detail.html',
                  {'activity': activity})



"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""
"""XXXXXXXXXXXX                                                       VIEW ACTIVITIES                                             XXXXXXXXXXX"""
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""
    
# @login_required
# def activity_list(request):
#     # # Get the current year and month from the query or from the current date
#     year = int(request.GET.get('year', timezone.now().year))
#     month = int(request.GET.get('month', timezone.now().month))
    
#     first_day = date(year, month, 1)
#     last_day = date(year, month, monthrange(year, month)[1])
    
#     # generate all date of month
#     days_in_month = [first_day + timedelta(days=i) for i in range((last_day - first_day).days + 1)]

    
#     # filter activities from user
#     activities = Activity.objects.filter(user=request.user)
        
#     calendar_data = []
#     for current_date in days_in_month:
#         day_activities = []
#         for activity in activities:
#             # Check if the activity should be on this day
#             if activity.is_within_date_range(current_date) and activity.is_scheduled_for_day(current_date):
#                 log = ActivityLog.objects.filter(activity=activity, date=current_date).first()
#                 if log is None:
#                     log = ActivityLog.get_or_create_log(activity, request.user, current_date)
#                 status = log.status if log else None
#                 print(f"Fecha: {current_date}, Actividad: {activity.name}, Estado: {status}")
#                 day_activities.append((activity, status, log))
#         calendar_data.append((current_date, day_activities))
        
#     # calculate next and previous months
#     previous_month = first_day - timedelta(days=1)
#     next_month = first_day + timedelta(days=32)
#     previous_month = previous_month.replace(day=1)
#     next_month = next_month.replace(day=1)

    
#     return render(request, 'prime/activity_list.html', {
#         'calendar_data': calendar_data,
#         'month': month,
#         'year': year,
#         'previous_month': previous_month,
#         'next_month': next_month,
#     })

@login_required
def activity_list(request):
    # # Get the current year and month from the query or from the current date
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    
    # generate all date of month
    days_in_month = [first_day + timedelta(days=i) for i in range((last_day - first_day).days + 1)]

    
    # filter activities from user
    activities = Activity.objects.filter(user=request.user)
        
    calendar_data = []
    for current_date in days_in_month:
        day_activities = []
        for activity in activities:
            # Check if the activity should be on this day
            log = ActivityLog.objects.filter(activity=activity, date=current_date).first()
            if log:
                status = log.status
                print(f"Fecha: {current_date}, Actividad: {activity.name}, Estado: {status}")
                day_activities.append((activity, status, log))
        calendar_data.append((current_date, day_activities))
        
    # calculate next and previous months
    previous_month = first_day - timedelta(days=1)
    next_month = first_day + timedelta(days=32)
    previous_month = previous_month.replace(day=1)
    next_month = next_month.replace(day=1)

    
    return render(request, 'prime/activity_list.html', {
        'calendar_data': calendar_data,
        'month': month,
        'year': year,
        'previous_month': previous_month,
        'next_month': next_month,
    })

    
    
    
# Mark activity as completed or incompleted

@login_required
def mark_activity(request, activity_id):
    if request.method == 'POST':
        raw_date = request.POST.get("date")
        
        # validate if raw_date exist before proceded
        if not raw_date:
            return HttpResponseForbidden("No se proporciionó una fecha válida.")
        
        try:
            # transform date to correct date format
            date = datetime.strptime(raw_date, '%Y-%m-%d').date()
        except ValueError:
            return HttpResponseForbidden("Fecha inválida. Asegurate de enviar la fecha en formato YYYY-MM-DD.")
        
        activity = get_object_or_404(Activity, id=activity_id, user=request.user)
        status = request.POST.get("status")
        
        # Validar y convertir la fecha al formato correcto
        try:
            date = datetime.strptime(raw_date, '%Y-%m-%d').date()
        except ValueError:
            return HttpResponseForbidden("Fecha inválida. Asegúrate de enviar la fecha en formato YYYY-MM-DD.")

        # create or update ActivityLog register
        ActivityLog.objects.update_or_create(
            activity=activity,
            date=date,
            user=request.user,
            defaults={'status': status}
        )
        
        return redirect('prime:activity_list')
        


# LOGS

@login_required
def delete_activity_log(request, log_id):
    log = get_object_or_404(ActivityLog, id=log_id, user=request.user)

    if request.method == "POST":
        print(f"Eliminando registro de ActivityLog con ID: {log_id}")
        log.delete()
        return redirect('prime:activity_list')

    return HttpResponseForbidden("Cannot delete this activity log.")

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
        start_date =activity.start_date or ActivityLog.objects.filter(activity=activity).earliest('date').date
        end_date = activity.end_date or ActivityLog.objects.filter(activity=activity).latest('date').date
        
        # active dates based on days of week
        expected_dates = [
            date for date in date_range(start_date, end_date)
            if date.strftime('%a')[:3] in activity.days_of_week.split()
        ]
        
        total_count = len(expected_dates)
        completed_count = ActivityLog.objects.filter(activity=activity, status= '✔️', date__range=(start_date, end_date)).count()
        incompleted_count = total_count - completed_count
        
        activity_stats.append({
            'name': activity.name,
            'total_count': total_count,
            'completed_count': completed_count,
            'incompleted_count': incompleted_count,
        })
        
        context = {'activity_stats': activity_stats}
    return render(request, 'prime/metrics.html', context)

        

