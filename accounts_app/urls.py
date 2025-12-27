from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register', views.RegisterView.as_view(), name='register'),
    path('login', views.LoginView.as_view(), name='login'),

    # Password Operations
    path('password/change', views.ChangePasswordView.as_view(), name='change-password'),
    path('password/forgot', views.ForgotPasswordRequestView.as_view(), name='forgot-password'),
    path('password/reset', views.ResetPasswordView.as_view(), name='reset-password'),

    # User (self)
    path('me', views.UserSelfRetrieveUpdateView.as_view(), name='user-self'),
]
