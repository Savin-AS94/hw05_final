from django import views
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.views import PasswordChangeDoneView
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetCompleteView
from django.urls import path
from . import views

app_name = 'users'

temp_1 = 'users/logged_out.html'
temp_2 = 'users/login.html'
temp_3 = 'users/password_change_form.html'
temp_4 = 'users/password_change_done.html'
temp_5 = 'users/password_reset_form.html'
temp_6 = 'users/password_reset_done.html'
temp_7 = 'users/password_reset_confirm.html'
temp_8 = 'users/password_reset_complete.html'

urlpatterns = [
    path('logout/',
         LogoutView.as_view(template_name=temp_1),
         name='logout'),
    path(
        'login/', LoginView.as_view(template_name=temp_2),
        name='login'
    ),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('password_change/', PasswordChangeView.as_view(template_name=temp_3),
         name='password_change'),
    path('password_change/done/',
         PasswordChangeDoneView.as_view(template_name=temp_4),
         name='password_done'),
    path('password_reset', PasswordResetView.as_view(template_name=temp_5),
         name='password_reset'),
    path('password_reset/done/',
         PasswordResetDoneView.as_view(template_name=temp_6),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name=temp_7),
         name='password_reset_confirm'),
    path('reset/done/',
         PasswordResetCompleteView.as_view(template_name=temp_8),
         name='password_reset_complete'), ]
