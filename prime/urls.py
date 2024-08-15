from django.urls import path

from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = "prime"


urlpatterns = [
    path('', views.home, name='home'),
    path('create-activity/', views.create_activity, name='create_activity'),
    path('metrics/', views.metrics, name='metrics'),
    path('login/', views.loginUsuario, name='login'),
    path('logout/', views.logoutUsuario, name='logout'),
    path('signup/', views.crearUsuario, name='crear_usuario'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),
    path('create-activity/', views.create_activity, name='create_activity'),
    path('activities/', views.activity_list, name='activity_list'),
    path('activities/<int:activity_id>/',
         views.activity_detail, name='activity_detail'),
    path('activities/<int:activity_id>/edit/',
         views.edit_activity, name='edit_activity'),
    path('activities/log/<int:log_id>/mark/',
         views.mark_activity, name='mark_activity'),
    path('activities/<int:activity_id>/delete/',
         views.delete_activity, name='delete_activity'),
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('get-events/', views.get_events, name='get_events'),
    path('activities/log/<int:log_id>/delete/',
         views.delete_activity_log, name='delete_activity_log'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
