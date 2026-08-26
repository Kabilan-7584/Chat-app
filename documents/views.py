import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.http import (
    require_GET,
    require_POST,
)

from .forms import DocumentUploadForm
from .models import (
    Document,
    DocumentConversation,
)
from .services.document_chat_service import (
    DocumentChatService,
)
from .services.document_processing_service import (
    DocumentProcessingService,
)


@login_required
@require_GET
def document_list(request):
    """
    Display documents owned by the authenticated user.
    """

    documents = (
        Document.objects
        .filter(
            user=request.user,
        )
        .order_by("-updated_at")
    )

    return render(
        request,
        "documents/document_list.html",
        {
            "documents": documents,
        },
    )


@login_required
def upload_document(request):
    """
    Display the upload form with GET.

    Process the uploaded PDF with POST.
    """

    if request.method == "POST":

        form = DocumentUploadForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            document = form.save(
                commit=False,
            )

            document.user = request.user

            document.filename = (
                document.file.name
            )

            document.status = (
                Document.ProcessingStatus.UPLOADED
            )

            document.save()

            try:

                DocumentProcessingService().process(
                    document
                )

            except RuntimeError:

                pass

            return redirect(
                "documents:document_list"
            )

    else:

        form = DocumentUploadForm()

    return render(
        request,
        "documents/upload.html",
        {
            "form": form,
        },
    )


@login_required
@require_GET
def document_chat_page(
    request,
    document_id,
):
    """
    Display the document-specific chat page.

    Only documents owned by the authenticated
    user can be opened.
    """

    document = get_object_or_404(
        Document,
        id=document_id,
        user=request.user,
    )

    conversations = (
        DocumentConversation.objects
        .filter(
            user=request.user,
            document=document,
        )
        .order_by("-updated_at")
    )

    return render(
        request,
        "documents/document_chat.html",
        {
            "document": document,
            "conversations": conversations,
        },
    )


@login_required
@require_POST
def create_conversation(
    request,
    document_id,
):
    """
    Create a conversation for a document owned
    by the authenticated user.
    """

    document = get_object_or_404(
        Document,
        id=document_id,
        user=request.user,
    )

    if document.status != (
        Document.ProcessingStatus.READY
    ):
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "This document is not ready "
                    "for chat."
                ),
            },
            status=400,
        )

    try:

        conversation = (
            DocumentChatService()
            .create_conversation(
                user=request.user,
                document=document,
            )
        )

    except PermissionError:

        return JsonResponse(
            {
                "success": False,
                "error": "Document not found.",
            },
            status=404,
        )

    return JsonResponse(
        {
            "success": True,
            "conversation": {
                "id": conversation.id,
                "title": conversation.title,
                "document_id": (
                    conversation.document_id
                ),
            },
        },
        status=201,
    )


@login_required
@require_GET
def conversation_messages(
    request,
    conversation_id,
):
    """
    Return messages belonging to a conversation
    owned by the authenticated user.
    """

    service = DocumentChatService()

    try:

        conversation = (
            service.get_conversation(
                user=request.user,
                conversation_id=conversation_id,
            )
        )

    except PermissionError:

        return JsonResponse(
            {
                "success": False,
                "error": "Conversation not found.",
            },
            status=404,
        )

    messages = (
        conversation.messages
        .order_by("created_at")
    )

    return JsonResponse(
        {
            "success": True,
            "conversation": {
                "id": conversation.id,
                "title": conversation.title,
                "document_id": (
                    conversation.document_id
                ),
            },
            "messages": [
                {
                    "id": message.id,
                    "role": message.role,
                    "content": message.content,
                    "created_at": (
                        message.created_at.isoformat()
                    ),
                }
                for message in messages
            ],
        }
    )


@login_required
@require_POST
def document_chat(
    request,
    conversation_id,
):
    """
    Send a question to a document conversation.
    """

    try:

        data = json.loads(
            request.body.decode("utf-8")
        )

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):

        return JsonResponse(
            {
                "success": False,
                "error": "Invalid request format.",
            },
            status=400,
        )

    service = DocumentChatService()

    try:

        result = service.send_message(
            user=request.user,
            conversation_id=conversation_id,
            content=data.get("message"),
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
                "error": "Conversation not found.",
            },
            status=404,
        )

    except RuntimeError:

        return JsonResponse(
            {
                "success": False,
                "error": (
                    "The document AI service is "
                    "temporarily unavailable. "
                    "Please try again."
                ),
            },
            status=503,
        )

    return JsonResponse(
        {
            "success": True,
            "message": {
                "id": (
                    result[
                        "assistant_message"
                    ].id
                ),
                "role": (
                    result[
                        "assistant_message"
                    ].role
                ),
                "content": (
                    result[
                        "assistant_message"
                    ].content
                ),
                "created_at": (
                    result[
                        "assistant_message"
                    ]
                    .created_at
                    .isoformat()
                ),
            },
            "sources": result.get(
                "sources",
                [],
            ),
        }
    )