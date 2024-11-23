from django.urls import path

from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = "prime"


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginUsuario, name='login'),
    path('create-activity/', views.create_activity, name='create_activity'),
    path('metrics/', views.metrics, name='metrics'),
    path('logout/', views.logoutUsuario, name='logout'),
    path('signup/', views.crearUsuario, name='crear_usuario'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),
    path('activities/', views.activity_list, name='activity_list'),
    path('activities/<int:activity_id>/', views.activity_detail, name='activity_detail'),
    path('activities/<int:activity_id>/delete/', views.delete_activity, name='delete_activity'),
    path('activities/delete-all/', views.delete_all_activities, name='delete_all_activities'),
    path('mark_acitvity/<int:activity_id>/', views.mark_activity, name='mark_activity'),
    path('activities/log/<int:log_id>/delete/', views.delete_activity_log, name='delete_activity_log'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
