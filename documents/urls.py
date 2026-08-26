from django.urls import path

from . import views


app_name = "documents"


urlpatterns = [
    path(
        "",
        views.document_list,
        name="document_list",
    ),

    path(
        "upload/",
        views.upload_document,
        name="upload",
    ),

    path(
        "<int:document_id>/chat/",
        views.document_chat_page,
        name="document_chat_page",
    ),

    path(
        "<int:document_id>/conversations/",
        views.create_conversation,
        name="create_conversation",
    ),

    path(
        "conversations/<int:conversation_id>/messages/",
        views.conversation_messages,
        name="conversation_messages",
    ),

    path(
        "conversations/<int:conversation_id>/chat/",
        views.document_chat,
        name="document_chat",
    ),
]