from django.urls import path

from . import views


app_name = "chatbot"


urlpatterns = [
    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "new/",
        views.create_thread,
        name="create_thread",
    ),

    path(
        "<int:thread_id>/messages/",
        views.thread_messages,
        name="thread_messages",
    ),

    path(
        "<int:thread_id>/message/",
        views.send_message,
        name="send_message",
    ),

    path(
        "<int:thread_id>/delete/",
        views.delete_thread,
        name="delete_thread",
    ),
]
