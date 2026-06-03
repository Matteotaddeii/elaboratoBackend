from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registrazione/', views.register_view, name='iscrizione'),
    path('profilo/', views.profile_view, name='profile'),
    path('profilo/cambia-password/', views.MyPasswordChangeView.as_view(), name='change_password'),
    path('gestione/utenti/', views.manager_users_list, name='manager_users'),
    path('gestione/utenti/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),
]