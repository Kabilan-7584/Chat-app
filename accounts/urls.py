from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import (
    accounts_home,
    protected_test_view,
    signup_view,
)


app_name = "accounts"


urlpatterns = [
    path("", accounts_home, name="home"),

    path(
        "signup/",
        signup_view,
        name="signup",
    ),

    path(
        "login/",
        LoginView.as_view(
            template_name="accounts/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),

    path(
        "protected/",
        protected_test_view,
        name="protected",
    ),
]