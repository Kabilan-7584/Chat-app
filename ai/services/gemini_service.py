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
            model="gemini-3.5-flash",
            temperature=1.0,
            max_retries=2,
            api_key=api_key,
        )

    def generate_response(self, prompt: str) -> str:
        """
        Send a prompt to Gemini and return the text response.
        """

        if not prompt or not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        try:
            response = self.llm.invoke(prompt)
            return response.text

        except Exception as exc:
            raise RuntimeError(
                "Gemini request failed."
            ) from exc