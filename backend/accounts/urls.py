from django.urls import re_path
from .views import (
    RegisterView,
    LoginView,
    RefreshTokenView,
    LogoutView,
    UserProfileView,
    ChangePasswordView,
    DeleteAccountView,
)

urlpatterns = [
    re_path(r'^register/?$', RegisterView.as_view(), name='auth-register'),
    re_path(r'^login/?$', LoginView.as_view(), name='auth-login'),
    re_path(r'^refresh/?$', RefreshTokenView.as_view(), name='auth-refresh'),
    re_path(r'^logout/?$', LogoutView.as_view(), name='auth-logout'),
    re_path(r'^me/?$', UserProfileView.as_view(), name='auth-me'),
    re_path(r'^profile/?$', UserProfileView.as_view(), name='auth-profile'),
    re_path(r'^change-password/?$', ChangePasswordView.as_view(), name='auth-change-password'),
    re_path(r'^delete-account/?$', DeleteAccountView.as_view(), name='auth-delete-account'),
]
