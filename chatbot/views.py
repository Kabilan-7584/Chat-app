import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .models import ChatThread
from .services.chat_service import ChatService


@login_required
@require_GET
def dashboard(request):
    """
    Display the chat dashboard.

    Only the authenticated user's threads are loaded.
    """

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
@require_POST
def create_thread(request):
    """
    Create a new chat thread for the authenticated user.
    """

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
    """
    Receive a user message and generate an AI response.
    """

    # -----------------------------------------
    # Find ONLY the authenticated user's thread
    # -----------------------------------------

    thread = get_object_or_404(
        ChatThread,
        id=thread_id,
        user=request.user,
    )

    # -----------------------------------------
    # Parse JSON
    # -----------------------------------------

    try:
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

    # -----------------------------------------
    # Extract message
    # -----------------------------------------

    content = data.get("message")

    # -----------------------------------------
    # Process through ChatService
    # -----------------------------------------

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

    # -----------------------------------------
    # Return assistant response
    # -----------------------------------------

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
