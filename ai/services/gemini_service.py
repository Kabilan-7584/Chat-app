import os

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_google_genai import ChatGoogleGenerativeAI


class GeminiService:
    """
    Reusable service for interacting with Google Gemini.
    """

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash-lite",
            api_key=api_key,

            # Faster responses for chat.
            thinking_level="low",

            # Prevent requests from hanging indefinitely.
            request_timeout=30,

            # Only one automatic retry.
            retries=1,
        )

    def generate_response(self, conversation) -> str:
        """
        Send a conversation to Gemini and return
        the assistant response.
        """

        if not conversation:
            raise ValueError(
                "Conversation cannot be empty."
            )

        messages = []

        for item in conversation:

            role = item.get("role")
            content = item.get("content")

            if not content:
                continue

            if role == "user":

                messages.append(
                    HumanMessage(
                        content=content
                    )
                )

            elif role == "assistant":

                messages.append(
                    AIMessage(
                        content=content
                    )
                )

            elif role == "system":

                messages.append(
                    SystemMessage(
                        content=content
                    )
                )

        if not messages:
            raise ValueError(
                "Conversation contains no valid messages."
            )

        try:

            response = self.llm.invoke(
                messages
            )

            response_text = response.text

            if not response_text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return response_text.strip()

        except Exception as exc:

            raise RuntimeError(
                "Gemini request failed."
            ) from exc
