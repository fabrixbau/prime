from django.urls import path

from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = "prime"


urlpatterns = [
    path('', views.home, name='home'),
    path('new-activity/', views.new_activity, name='new_activity'),
    path('metrics/', views.metrics, name='metrics'),
    path('login/', views.loginUsuario, name='login'),
    path('logout/', views.logoutUsuario, name='logout'),
    path('signup/', views.crearUsuario, name='crear_usuario'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),
    path('create-activity/', views.create_activity, name='create_activity'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
