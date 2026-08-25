import os

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
            temperature=0,
            max_retries=2,
            request_timeout=60,
            api_key=api_key,
            thinking_level="minimal",
        )

    def generate_response(self, messages):

        if not messages:
            raise ValueError(
                "Messages cannot be empty."
            )

        try:

            response = self.llm.invoke(
                messages
            )

            return response.text

        except Exception as exc:

            raise RuntimeError(
                "Gemini request failed."
            ) from exc
