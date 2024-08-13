from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .models import Activity
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

# Create your views here.

""" VISTA PRINCIPAL """


def home(request):
    user_profile = None
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)

    return render(request, 'prime/home.html', {'user_profile': user_profile})


def new_activity(request):
    if request.method == 'POST':
        # Handle the creation of a new activity
        pass
    return render(request, 'prime/new_activity.html')


def metrics(request):
    # Gather and pass metrics data to the template
    context = {
        'completed_activities': 5,  # Example data
        'missed_activities': 2,     # Example data
    }
    return render(request, 'prime/metrics.html', context)


def crearUsuario(request):
    if request.method == "POST":
        dataUsuario = request.POST["nuevoUsuario"]
        dataPassword = request.POST["nuevoPassword"]
        # Assuming you collect an email as well
        dataEmail = request.POST["email"]

        nuevoUsuario = User.objects.create_user(
            username=dataUsuario, password=dataPassword, email=dataEmail
        )
        if nuevoUsuario is not None:
            login(request, nuevoUsuario)
            return redirect("/complete-profile")

    return render(request, "prime/crear_usuario.html")


def loginUsuario(request):
    paginaDestino = request.GET.get("next", "/")
    context = {"destino": paginaDestino}

    if request.method == "POST":
        dataUsuario = request.POST["usuario"]
        dataPassword = request.POST["password"]
        dataDestino = request.POST.get("destino", "/")

        usuarioAuth = authenticate(
            request, username=dataUsuario, password=dataPassword)
        if usuarioAuth is not None:
            login(request, usuarioAuth)
            return redirect(dataDestino if dataDestino else "/")
        else:
            context = {"mensajeError": "Datos incorrectos"}

    return render(request, "prime/login.html", context)


def logoutUsuario(request):
    logout(request)
    return redirect("/")


@login_required
def complete_profile(request):
    if request.method == "POST":
        request.user.last_name = request.POST["lastname"]
        request.user.save()

        user_profile, created = UserProfile.objects.get_or_create(
            user=request.user)
        user_profile.nickname = request.POST["nickname"]
        user_profile.age = request.POST["age"]
        user_profile.save()

        return redirect("/")

    return render(request, "prime/complete_profile.html")


@login_required
def create_activity(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        days_of_week = request.POST['days_of_week']
        duration_minutes = request.POST['duration_minutes']
        start_time = request.POST['start_time']

        # Crea una nueva actividad y la asocia con el usuario actual
        Activity.objects.create(
            name=name,
            description=description,
            days_of_week=days_of_week,
            duration_minutes=duration_minutes,
            start_time=start_time,
            user=request.user
        )

        # Redirige al usuario a la página principal después
        return redirect('prime:home')

    # Si no es POST, redirige a la página de creación
    return HttpResponseRedirect('create_activity')


@login_required
def activity_list(request):
    # Obtener todas las actividades del usuario actual
    activities = Activity.objects.filter(
        user=request.user).order_by('start_time')

    # Organizar actividades por días de la semana
    days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    activities_by_day = {day: [] for day in days_of_week}
    for activity in activities:
        for day in activity.days_of_week.split():
            activities_by_day[day].append(activity)

    # Pasar las actividades organizadas al template
    return render(request, 'prime/activity_list.html',
                  {'activities_by_day': activities_by_day})


@login_required
def activity_detail(request, activity_id):
    # Obtener la actividad específica por ID
    activity = get_object_or_404(Activity, id=activity_id, user=request.user)
    return render(request, 'prime/activity_detail.html',
                  {'activity': activity})


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
        'Sun': 'Sunday'
    }

    if request.method == 'POST':
        activity.name = request.POST['name']
        activity.description = request.POST['description']
        activity.days_of_week = " ".join(request.POST.getlist('days_of_week'))
        activity.duration_minutes = request.POST['duration_minutes']
        activity.start_time = request.POST['start_time']
        activity.save()

        return redirect('prime:activity_detail', activity_id=activity.id)

    return render(request, 'prime/edit_activity.html', {
        'activity': activity,
        'days_of_week_choices': days_of_week_choices
    })
