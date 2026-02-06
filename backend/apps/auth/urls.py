"""
URL configuration for authentication endpoints.
"""

from django.urls import path

from .views import LogoutView, MeView, SigninView, SignupView, TokenRefreshView

app_name = "auth"

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("signin/", SigninView.as_view(), name="signin"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
]
