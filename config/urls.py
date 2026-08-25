from django.contrib import admin
from django.urls import include, path


urlpatterns = [

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
