from django.db import transaction

from chatbot.models import ChatThread, Message
from ai.services.gemini_service import GeminiService


class ChatService:
    """
    Business logic for authenticated chat conversations.

    Responsible for:
    - validating messages
    - verifying thread ownership
    - retrieving conversation history
    - constructing conversation context
    - calling Gemini
    - persisting messages
    """

    MAX_MESSAGE_LENGTH = 4000

    def __init__(self):
        self.gemini_service = GeminiService()

    def _validate_message(self, content):
        if not isinstance(content, str):
            raise ValueError("Message must be a string.")

        content = content.strip()

        if not content:
            raise ValueError("Message cannot be empty.")

        if len(content) > self.MAX_MESSAGE_LENGTH:
            raise ValueError(
                f"Message cannot exceed "
                f"{self.MAX_MESSAGE_LENGTH} characters."
            )

        return content

    def _verify_thread_ownership(self, user, thread):
        if thread.user_id != user.id:
            raise PermissionError(
                "You do not have access to this chat thread."
            )

    def _build_conversation_context(self, thread, current_message):
        """
        Build the ordered conversation context for Gemini.

        Previous messages are retrieved from this thread only.
        The current user message is appended last.
        """

        previous_messages = (
            Message.objects
            .filter(thread=thread)
            .order_by("created_at", "id")
        )

        conversation = []

        for message in previous_messages:
            conversation.append(
                {
                    "role": message.role,
                    "content": message.content,
                }
            )

        conversation.append(
            {
                "role": Message.Role.USER,
                "content": current_message,
            }
        )

        return conversation

    @transaction.atomic
    def send_message(self, user, thread, content):
        """
        Send a user message using the full conversation context.
        """

        self._verify_thread_ownership(user, thread)

        content = self._validate_message(content)

        conversation = self._build_conversation_context(
            thread=thread,
            current_message=content,
        )

        try:
            ai_response = self.gemini_service.generate_response(
                conversation
            )

        except Exception as exc:
            raise RuntimeError(
                "Unable to generate an AI response."
            ) from exc

        if not isinstance(ai_response, str):
            raise RuntimeError(
                "AI returned an invalid response."
            )

        ai_response = ai_response.strip()

        if not ai_response:
            raise RuntimeError(
                "AI returned an empty response."
            )

        user_message = Message.objects.create(
            thread=thread,
            role=Message.Role.USER,
            content=content,
        )

        assistant_message = Message.objects.create(
            thread=thread,
            role=Message.Role.ASSISTANT,
            content=ai_response,
        )

        thread.save(update_fields=["updated_at"])

        return {
            "user_message": user_message,
            "assistant_message": assistant_message,
        }
