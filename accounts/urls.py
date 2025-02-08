from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView,PasswordChangeView,PasswordChangeDoneView
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    # path('profile/', views.profile, name='profile'),
    path('profile/passwordchange/', PasswordChangeView.as_view(template_name='passwordchange.html'), name='passwordchange.html'),
    path('password-change-done/', PasswordChangeDoneView.as_view(template_name='password_change_done.html'),
         name='password_change_done'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
]