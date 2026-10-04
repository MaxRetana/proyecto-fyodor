from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='users/login.html', redirect_authenticated_user=True),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-change/', views.UserPasswordChangeView.as_view(), name='password-change'),
    path('my-preferences/', views.MyPreferencesView.as_view(), name='my-preferences'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('settings/create/', views.UserCreateView.as_view(), name='user-create'),
    path('settings/<int:pk>/', views.UserSettingsView.as_view(), name='user-settings'),
]
