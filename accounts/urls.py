from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView,PasswordChangeView,PasswordChangeDoneView
urlpatterns = [
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('signup/', views.UserRegisterView.as_view(), name='signup'),
    path('verify/', views.UserRegisterVerifyCodeView.as_view(), name='verify_code'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('resend_code/', views.ResendOtpCodeView.as_view(), name='resend_code'),
    path('login/verify/', views.UserLoginVerifyView.as_view(), name='verify_login_code'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),


    path('profile/passwordchange/', PasswordChangeView.as_view(template_name='passwordchange.html'), name='passwordchange.html'),
    path('password-change-done/', PasswordChangeDoneView.as_view(template_name='password_change_done.html'),
         name='password_change_done'),

]