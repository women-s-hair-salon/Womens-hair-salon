from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    # path('', views.homeView.as_view(), name='home'),
    path('home/', views.home_view, name='home'),
    # path('login/', auth_views.LoginView.as_view(template_name='salon/login.html'), name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    # path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    # path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
]