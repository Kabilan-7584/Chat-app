from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView


urlpatterns = [

    path(
        "",
        RedirectView.as_view(
            pattern_name="accounts:login",
            permanent=False,
        ),
    ),

    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "accounts/",
        include("accounts.urls"),
    ),

    path(
        "chat/",
        include("chatbot.urls"),
    ),

    path(
        "documents/",
        include("documents.urls"),
    ),
]