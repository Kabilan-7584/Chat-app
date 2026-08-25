import os

from django.test import SimpleTestCase

from ai.services.gemini_service import GeminiService


class GeminiServiceTests(SimpleTestCase):

    def test_gemini_service_requires_api_key(self):
        original_key = os.environ.get("GEMINI_API_KEY")

        try:
            os.environ.pop("GEMINI_API_KEY", None)

            with self.assertRaises(RuntimeError):
                GeminiService()

        finally:
            if original_key is not None:
                os.environ["GEMINI_API_KEY"] = original_key