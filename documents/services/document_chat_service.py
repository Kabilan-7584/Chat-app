from django.db import transaction

from documents.models import (
    DocumentConversation,
    DocumentMessage,
)

from .rag_service import RAGService


class DocumentChatService:
    """
    Handles document-specific conversations.

    Flow:

    User Question
        ↓
    Conversation History
        ↓
    Retriever
        ↓
    Relevant Document Context
        ↓
    Gemini
        ↓
    Save User Message
        ↓
    Save Assistant Message
    """

    MAX_MESSAGE_LENGTH = 10000

    def __init__(self, rag_service=None):
        self.rag_service = (
            rag_service
            or RAGService()
        )

    def create_conversation(
        self,
        *,
        user,
        document,
        title="New Conversation",
    ):
        self._verify_document_ownership(
            user=user,
            document=document,
        )

        return DocumentConversation.objects.create(
            user=user,
            document=document,
            title=(
                title.strip()
                if isinstance(title, str)
                and title.strip()
                else "New Conversation"
            ),
        )

    def get_conversation(
        self,
        *,
        user,
        conversation_id,
    ):
        conversation = (
            DocumentConversation.objects
            .select_related(
                "document",
            )
            .filter(
                id=conversation_id,
                user=user,
                document__user=user,
            )
            .first()
        )

        if conversation is None:
            raise PermissionError(
                "You do not have access to this conversation."
            )

        return conversation

    def get_messages(
        self,
        *,
        user,
        conversation_id,
    ):
        conversation = self.get_conversation(
            user=user,
            conversation_id=conversation_id,
        )

        return (
            conversation.messages
            .order_by("created_at")
        )

    @transaction.atomic
    def send_message(
        self,
        *,
        user,
        conversation_id,
        content,
    ):
        conversation = self.get_conversation(
            user=user,
            conversation_id=conversation_id,
        )

        content = self._validate_message(
            content
        )

        history = list(
            conversation.messages
            .order_by("created_at")
            .values(
                "role",
                "content",
            )
        )

        user_message = (
            DocumentMessage.objects.create(
                conversation=conversation,
                role=DocumentMessage.Role.USER,
                content=content,
            )
        )

        try:
            response = self.rag_service.answer(
                user_id=user.id,
                document_id=(
                    conversation.document_id
                ),
                query=content,
                conversation_history=history,
            )

        except Exception as exc:
            raise RuntimeError(
                "Unable to generate document response."
            ) from exc

        answer = response.get("answer")

        if not isinstance(answer, str):
            raise RuntimeError(
                "The AI returned an invalid response."
            )

        answer = answer.strip()

        if not answer:
            raise RuntimeError(
                "The AI returned an empty response."
            )

        assistant_message = (
            DocumentMessage.objects.create(
                conversation=conversation,
                role=DocumentMessage.Role.ASSISTANT,
                content=answer,
            )
        )

        conversation.save(
            update_fields=[
                "updated_at",
            ]
        )

        return {
            "conversation": conversation,
            "user_message": user_message,
            "assistant_message": assistant_message,
            "sources": response.get(
                "sources",
                [],
            ),
        }

    @classmethod
    def _validate_message(
        cls,
        content,
    ):
        if not isinstance(content, str):
            raise ValueError(
                "Message must be a string."
            )

        content = content.strip()

        if not content:
            raise ValueError(
                "Message cannot be empty."
            )

        if len(content) > cls.MAX_MESSAGE_LENGTH:
            raise ValueError(
                "Message is too long."
            )

        return content

    @staticmethod
    def _verify_document_ownership(
        *,
        user,
        document,
    ):
        if document.user_id != user.id:
            raise PermissionError(
                "You do not have access to this document."
            )