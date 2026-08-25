from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from chatbot.models import ChatThread, Message
from chatbot.services.chat_service import ChatService


User = get_user_model()


class ChatServiceTests(TestCase):

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
            title="Other Chat",
        )


    @patch(
        "chatbot.services.chat_service.GeminiService.generate_response"
    )
    def test_send_message_success(
        self,
        mock_generate,
    ):

        mock_generate.return_value = (
            "Django is a Python web framework."
        )

        result = ChatService().send_message(
            user=self.user,
            thread=self.thread,
            content="What is Django?",
        )

        self.assertEqual(
            result["user_message"].role,
            Message.Role.USER,
        )

        self.assertEqual(
            result["assistant_message"].role,
            Message.Role.ASSISTANT,
        )

        self.assertEqual(
            result["assistant_message"].content,
            "Django is a Python web framework.",
        )

        self.assertEqual(
            self.thread.messages.count(),
            2,
        )

        mock_generate.assert_called_once_with(
            "What is Django?"
        )


    def test_empty_message_is_rejected(self):

        with self.assertRaises(ValueError):
            ChatService().send_message(
                user=self.user,
                thread=self.thread,
                content="   ",
            )

        self.assertEqual(
            self.thread.messages.count(),
            0,
        )


    def test_message_too_long_is_rejected(self):

        long_message = "a" * 10001

        with self.assertRaises(ValueError):
            ChatService().send_message(
                user=self.user,
                thread=self.thread,
                content=long_message,
            )

        self.assertEqual(
            self.thread.messages.count(),
            0,
        )


    def test_other_users_thread_is_rejected(self):

        with self.assertRaises(PermissionError):
            ChatService().send_message(
                user=self.user,
                thread=self.other_thread,
                content="Hello",
            )

        self.assertEqual(
            self.other_thread.messages.count(),
            0,
        )


    @patch(
        "chatbot.services.chat_service.GeminiService.generate_response"
    )
    def test_gemini_failure_is_handled(
        self,
        mock_generate,
    ):

        mock_generate.side_effect = Exception(
            "Gemini unavailable"
        )

        with self.assertRaises(RuntimeError):
            ChatService().send_message(
                user=self.user,
                thread=self.thread,
                content="Hello",
            )

        self.assertEqual(
            self.thread.messages.count(),
            0,
        )


    @patch(
        "chatbot.services.chat_service.GeminiService.generate_response"
    )
    def test_empty_ai_response_is_rejected(
        self,
        mock_generate,
    ):

        mock_generate.return_value = ""

        with self.assertRaises(RuntimeError):
            ChatService().send_message(
                user=self.user,
                thread=self.thread,
                content="Hello",
            )

        self.assertEqual(
            self.thread.messages.count(),
            0,
        )
