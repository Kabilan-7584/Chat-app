from chatbot.models import Message
from ai.services.gemini_service import GeminiService


class ChatService:
    """
    Application service responsible for processing chat messages.

    Conversation memory is implemented by loading previous
    messages from the current thread and sending them to Gemini.
    """

    MAX_MESSAGE_LENGTH = 10000
    MAX_HISTORY_MESSAGES = 20

    def __init__(self):
        self.gemini_service = GeminiService()

    def send_message(self, user, thread, content):
        """
        Validate the request, load conversation history,
        save the user message, generate an AI response,
        and save the assistant message.
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
        # 3. Load previous conversation
        # -----------------------------------------

        previous_messages = (
            Message.objects
            .filter(thread=thread)
            .order_by("-created_at")[
                :self.MAX_HISTORY_MESSAGES
            ]
        )

        previous_messages = list(
            reversed(previous_messages)
        )

        conversation = []

        for message in previous_messages:

            if message.role == Message.Role.USER:
                role = "user"

            elif message.role == Message.Role.ASSISTANT:
                role = "assistant"

            elif message.role == Message.Role.SYSTEM:
                role = "system"

            else:
                continue

            conversation.append(
                {
                    "role": role,
                    "content": message.content,
                }
            )

        # -----------------------------------------
        # 4. Save current user message
        # -----------------------------------------

        user_message = Message.objects.create(
            thread=thread,
            role=Message.Role.USER,
            content=content,
        )

        # Add current message to conversation
        conversation.append(
            {
                "role": "user",
                "content": content,
            }
        )

        # -----------------------------------------
        # 5. Send complete conversation to Gemini
        # -----------------------------------------

        try:

            assistant_content = (
                self.gemini_service.generate_response(
                    conversation
                )
            )

        except Exception as exc:

            user_message.delete()

            raise RuntimeError(
                "Unable to generate an AI response."
            ) from exc

        # -----------------------------------------
        # 6. Validate AI response
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
        # 7. Save assistant response
        # -----------------------------------------

        assistant_message = Message.objects.create(
            thread=thread,
            role=Message.Role.ASSISTANT,
            content=assistant_content,
        )

        # -----------------------------------------
        # 8. Update thread timestamp
        # -----------------------------------------

        thread.save(
            update_fields=["updated_at"]
        )

        return {
            "user_message": user_message,
            "assistant_message": assistant_message,
        }
