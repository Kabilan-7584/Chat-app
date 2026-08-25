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
            password="TestPassword123!",
        )

        self.thread = ChatThread.objects.create(
            user=self.user,
            title="Test Chat",
        )

        self.service = ChatService()

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

        result = self.service.send_message(
            user=self.user,
            thread=self.thread,
            content="What is Django?",
        )

        mock_generate.assert_called_once_with(
            [
                {
                    "role": "user",
                    "content": "What is Django?",
                }
            ]
        )

        self.assertEqual(
            result["user_message"].content,
            "What is Django?",
        )

        self.assertEqual(
            result["assistant_message"].content,
            "Django is a Python web framework.",
        )

        self.assertEqual(
            Message.objects.filter(
                thread=self.thread
            ).count(),
            2,
        )

    @patch(
        "chatbot.services.chat_service.GeminiService.generate_response"
    )
    def test_previous_messages_are_sent_to_gemini(
        self,
        mock_generate,
    ):

        Message.objects.create(
            thread=self.thread,
            role=Message.Role.USER,
            content="What is Python?",
        )

        Message.objects.create(
            thread=self.thread,
            role=Message.Role.ASSISTANT,
            content="Python is a programming language.",
        )

        mock_generate.return_value = (
            "Python is useful for many types of development."
        )

        self.service.send_message(
            user=self.user,
            thread=self.thread,
            content="Why is it popular?",
        )

        mock_generate.assert_called_once_with(
            [
                {
                    "role": "user",
                    "content": "What is Python?",
                },
                {
                    "role": "assistant",
                    "content": "Python is a programming language.",
                },
                {
                    "role": "user",
                    "content": "Why is it popular?",
                },
            ]
        )

    def test_empty_message_is_rejected(self):

        with self.assertRaises(ValueError):

            self.service.send_message(
                user=self.user,
                thread=self.thread,
                content="",
            )

    def test_whitespace_message_is_rejected(self):

        with self.assertRaises(ValueError):

            self.service.send_message(
                user=self.user,
                thread=self.thread,
                content="   ",
            )

    def test_message_too_long_is_rejected(self):

        long_message = (
            "x"
            * (
                ChatService.MAX_MESSAGE_LENGTH
                + 1
            )
        )

        with self.assertRaises(ValueError):

            self.service.send_message(
                user=self.user,
                thread=self.thread,
                content=long_message,
            )

    def test_non_string_message_is_rejected(self):

        with self.assertRaises(ValueError):

            self.service.send_message(
                user=self.user,
                thread=self.thread,
                content=None,
            )

    def test_wrong_user_is_rejected(self):

        other_user = User.objects.create_user(
            username="otheruser",
            password="OtherPassword123!",
        )

        with self.assertRaises(PermissionError):

            self.service.send_message(
                user=other_user,
                thread=self.thread,
                content="Hello",
            )

    @patch(
        "chatbot.services.chat_service.GeminiService.generate_response"
    )
    def test_gemini_failure_does_not_leave_user_message(
        self,
        mock_generate,
    ):

        mock_generate.side_effect = RuntimeError(
            "Gemini failed"
        )

        with self.assertRaises(RuntimeError):

            self.service.send_message(
                user=self.user,
                thread=self.thread,
                content="Hello",
            )

        self.assertEqual(
            Message.objects.filter(
                thread=self.thread
            ).count(),
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

            self.service.send_message(
                user=self.user,
                thread=self.thread,
                content="Hello",
            )

        self.assertEqual(
            Message.objects.filter(
                thread=self.thread
            ).count(),
            0,
        )


    @patch(
        "chatbot.services.chat_service.GeminiService.generate_response"
    )
    def test_multi_turn_context_is_preserved(
        self,
        mock_generate,
    ):

        Message.objects.create(
            thread=self.thread,
            role=Message.Role.USER,
            content="What is Python?",
        )

        Message.objects.create(
            thread=self.thread,
            role=Message.Role.ASSISTANT,
            content="Python is a programming language.",
        )

        mock_generate.return_value = (
            "Python was created by Guido van Rossum."
        )

        self.service.send_message(
            user=self.user,
            thread=self.thread,
            content="Who created it?",
        )

        mock_generate.assert_called_once_with(
            [
                {
                    "role": "user",
                    "content": "What is Python?",
                },
                {
                    "role": "assistant",
                    "content": "Python is a programming language.",
                },
                {
                    "role": "user",
                    "content": "Who created it?",
                },
            ]
        )
