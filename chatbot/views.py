from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .models import ChatThread, Message
from .services.chat_service import ChatService


@login_required
@require_GET
def dashboard(request):
    threads = (
        ChatThread.objects
        .filter(user=request.user)
        .order_by("-updated_at")
    )

    current_thread = threads.first()

    if current_thread is None:
        current_thread = ChatThread.objects.create(
            user=request.user,
            title="New Chat",
        )

        threads = [current_thread]

    return render(
        request,
        "chatbot/dashboard.html",
        {
            "threads": threads,
            "current_thread": current_thread,
        },
    )


@login_required
@require_GET
def thread_messages(request, thread_id):

    thread = get_object_or_404(
        ChatThread,
        id=thread_id,
        user=request.user,
    )

    messages = (
        Message.objects
        .filter(thread=thread)
        .order_by("created_at", "id")
    )

    return JsonResponse(
        {
            "success": True,
            "thread": {
                "id": thread.id,
                "title": thread.title,
            },
            "messages": [
                {
                    "id": message.id,
                    "role": message.role,
                    "content": message.content,
                    "created_at": message.created_at.isoformat(),
                }
                for message in messages
            ],
        }
    )


@login_required
@require_POST
def create_thread(request):

    thread = ChatThread.objects.create(
        user=request.user,
        title="New Chat",
    )

    return JsonResponse(
        {
            "success": True,
            "thread": {
                "id": thread.id,
                "title": thread.title,
            },
        },
        status=201,
    )


@login_required
@require_POST
def send_message(request, thread_id):

    thread = get_object_or_404(
        ChatThread,
        id=thread_id,
        user=request.user,
    )

    try:
        import json

        data = json.loads(
            request.body.decode("utf-8")
        )

    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {
                "success": False,
                "error": "Invalid request format.",
            },
            status=400,
        )

    content = data.get("message")

    try:

        result = ChatService().send_message(
            user=request.user,
            thread=thread,
            content=content,
        )

    except ValueError as exc:

        return JsonResponse(
            {
                "success": False,
                "error": str(exc),
            },
            status=400,
        )

    except PermissionError:

        return JsonResponse(
            {
                "success": False,
                "error": "You do not have access to this chat.",
            },
            status=404,
        )

    except RuntimeError:

        return JsonResponse(
            {
                "success": False,
                "error": (
                    "The AI service is temporarily "
                    "unavailable. Please try again."
                ),
            },
            status=503,
        )

    except Exception:

        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Something went wrong. "
                    "Please try again."
                ),
            },
            status=500,
        )

    assistant_message = result[
        "assistant_message"
    ]

    return JsonResponse(
        {
            "success": True,
            "message": {
                "id": assistant_message.id,
                "role": assistant_message.role,
                "content": assistant_message.content,
                "created_at": (
                    assistant_message.created_at.isoformat()
                ),
            },
        }
    )


@login_required
@require_http_methods(["DELETE"])
def delete_thread(request, thread_id):

    thread = get_object_or_404(
        ChatThread,
        id=thread_id,
        user=request.user,
    )

    thread.delete()

    return JsonResponse(
        {
            "success": True,
            "message": "Chat deleted successfully.",
        }
    )
