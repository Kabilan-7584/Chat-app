from chatbot.models import Message
from ai.services.gemini_service import GeminiService


class ChatService:
    """
    Application service responsible for processing chat messages.

    Conversation memory is intentionally NOT implemented yet.
    Only the current user message is sent to Gemini.
    """

    MAX_MESSAGE_LENGTH = 10000

    def __init__(self):
        self.gemini_service = GeminiService()

    def send_message(self, user, thread, content):
        """
        Validate the request, save the user message,
        generate an AI response, and save the assistant message.
        """

        # -----------------------------------------
        # 1. Ownership validation
        # -----------------------------------------

        if thread.user_id != user.id:
            raise PermissionError(
                "You do not have access to this chat thread."
            )

        # -----------------------------------------
        # 2. Input validation
        # -----------------------------------------

        if not isinstance(content, str):
            raise ValueError(
                "Message must be a string."
            )

        content = content.strip()

        if not content:
            raise ValueError(
                "Message cannot be empty."
            )

        if len(content) > self.MAX_MESSAGE_LENGTH:
            raise ValueError(
                f"Message cannot exceed "
                f"{self.MAX_MESSAGE_LENGTH} characters."
            )

        # -----------------------------------------
        # 3. Save user message
        # -----------------------------------------

        user_message = Message.objects.create(
            thread=thread,
            role=Message.Role.USER,
            content=content,
        )

        # -----------------------------------------
        # 4. Call common Gemini service
        # -----------------------------------------

        try:
            assistant_content = (
                self.gemini_service.generate_response(
                    content
                )
            )

        except Exception as exc:
            # Do not leave a user message behind
            # when AI generation completely fails.
            user_message.delete()

            raise RuntimeError(
                "Unable to generate an AI response."
            ) from exc

        # -----------------------------------------
        # 5. Validate AI response
        # -----------------------------------------

        if not assistant_content:
            user_message.delete()

            raise RuntimeError(
                "The AI returned an empty response."
            )

        assistant_content = str(
            assistant_content
        ).strip()

        if not assistant_content:
            user_message.delete()

            raise RuntimeError(
                "The AI returned an empty response."
            )

        # -----------------------------------------
        # 6. Save assistant message
        # -----------------------------------------

        assistant_message = Message.objects.create(
            thread=thread,
            role=Message.Role.ASSISTANT,
            content=assistant_content,
        )

        # -----------------------------------------
        # 7. Update thread timestamp
        # -----------------------------------------

        thread.save(
            update_fields=["updated_at"]
        )

        return {
            "user_message": user_message,
            "assistant_message": assistant_message,
        }
