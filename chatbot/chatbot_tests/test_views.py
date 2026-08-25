import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from chatbot.models import ChatThread, Message


User = get_user_model()


class ChatViewTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser",
            password="StrongPassword123!",
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            password="StrongPassword123!",
        )

        self.thread = ChatThread.objects.create(
            user=self.user,
            title="Test Chat",
        )

        self.other_thread = ChatThread.objects.create(
            user=self.other_user,
            title="Private Chat",
        )


    def test_dashboard_requires_login(self):

        response = self.client.get(
            reverse("chatbot:dashboard")
        )

        self.assertEqual(
            response.status_code,
            302,
        )


    def test_authenticated_user_can_open_dashboard(self):

        self.client.login(
            username="testuser",
            password="StrongPassword123!",
        )

        response = self.client.get(
            reverse("chatbot:dashboard")
        )

        self.assertEqual(
            response.status_code,
            200,
        )


    def test_user_can_create_thread(self):

        self.client.login(
            username="testuser",
            password="StrongPassword123!",
        )

        response = self.client.post(
            reverse("chatbot:create_thread")
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertTrue(
            response.json()["success"]
        )


    @patch(
        "chatbot.services.chat_service.GeminiService.generate_response"
    )
    def test_user_can_send_message(
        self,
        mock_generate,
    ):

        mock_generate.return_value = (
            "This is an AI response."
        )

        self.client.login(
            username="testuser",
            password="StrongPassword123!",
        )

        response = self.client.post(
            reverse(
                "chatbot:send_message",
                kwargs={
                    "thread_id": self.thread.id,
                },
            ),
            data=json.dumps(
                {
                    "message": "Hello Gemini",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertTrue(
            data["success"]
        )

        self.assertEqual(
            data["message"]["role"],
            "assistant",
        )


    def test_empty_message_returns_400(self):

        self.client.login(
            username="testuser",
            password="StrongPassword123!",
        )

        response = self.client.post(
            reverse(
                "chatbot:send_message",
                kwargs={
                    "thread_id": self.thread.id,
                },
            ),
            data=json.dumps(
                {
                    "message": "   ",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )


    def test_other_users_thread_is_not_accessible(self):

        self.client.login(
            username="testuser",
            password="StrongPassword123!",
        )

        response = self.client.post(
            reverse(
                "chatbot:send_message",
                kwargs={
                    "thread_id": self.other_thread.id,
                },
            ),
            data=json.dumps(
                {
                    "message": "Trying to access another user's chat",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(
            response.status_code,
            404,
        )


    def test_invalid_json_returns_400(self):

        self.client.login(
            username="testuser",
            password="StrongPassword123!",
        )

        response = self.client.post(
            reverse(
                "chatbot:send_message",
                kwargs={
                    "thread_id": self.thread.id,
                },
            ),
            data="not valid json",
            content_type="application/json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )


    @patch(
        "chatbot.services.chat_service.GeminiService.generate_response"
    )
    def test_gemini_failure_returns_503(
        self,
        mock_generate,
    ):

        mock_generate.side_effect = Exception(
            "Gemini unavailable"
        )

        self.client.login(
            username="testuser",
            password="StrongPassword123!",
        )

        response = self.client.post(
            reverse(
                "chatbot:send_message",
                kwargs={
                    "thread_id": self.thread.id,
                },
            ),
            data=json.dumps(
                {
                    "message": "Hello",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(
            response.status_code,
            503,
        )
