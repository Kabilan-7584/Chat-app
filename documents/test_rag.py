from unittest import TestCase
from unittest.mock import MagicMock

from documents.services.rag_service import (
    RAGService,
)


class RAGServiceTests(TestCase):

    def setUp(self):

        self.retriever = MagicMock()
        self.gemini = MagicMock()

        self.service = RAGService(
            retriever_service=self.retriever,
            gemini_service=self.gemini,
        )

    def test_empty_query_is_rejected(self):

        with self.assertRaises(
            ValueError
        ):
            self.service.answer(
                user_id=1,
                query="",
            )

    def test_missing_user_is_rejected(self):

        with self.assertRaises(
            ValueError
        ):
            self.service.answer(
                user_id=None,
                query="What is Python?",
            )

    def test_context_is_built_correctly(self):

        results = [
            {
                "id": "document-1-chunk-0",
                "content": (
                    "Python was created by "
                    "Guido van Rossum."
                ),
                "metadata": {
                    "filename": "python.pdf",
                    "page_number": 1,
                    "chunk_index": 0,
                },
                "distance": 0.1,
            }
        ]

        context = (
            self.service._build_context(
                results
            )
        )

        self.assertIn(
            "Python was created by Guido van Rossum.",
            context,
        )

        self.assertIn(
            "python.pdf",
            context,
        )

    def test_empty_retrieval_is_supported(self):

        context = (
            self.service._build_context([])
        )

        self.assertIn(
            "No relevant information",
            context,
        )

    def test_grounding_prompt_contains_rules(self):

        prompt = (
            self.service._build_prompt(
                query="Who created Python?",
                context="Python was created by Guido.",
            )
        )

        self.assertIn(
            "ONLY",
            prompt,
        )

        self.assertIn(
            "Do not invent",
            prompt,
        )

        self.assertIn(
            "not supported",
            prompt,
        )

    def test_retriever_is_called(self):

        self.retriever.retrieve.return_value = []

        self.gemini.generate_response.return_value = (
            "The documents do not provide enough "
            "information to answer this question."
        )

        self.service.answer(
            user_id=1,
            query="What is Python?",
            document_id=10,
            top_k=3,
        )

        self.retriever.retrieve.assert_called_once_with(
            user_id=1,
            query="What is Python?",
            document_id=10,
            top_k=3,
        )

    def test_gemini_receives_grounded_prompt(self):

        self.retriever.retrieve.return_value = [
            {
                "id": "document-1-chunk-0",
                "content": (
                    "Python was created by "
                    "Guido van Rossum."
                ),
                "metadata": {
                    "filename": "python.pdf",
                    "page_number": 1,
                    "chunk_index": 0,
                },
                "distance": 0.1,
            }
        ]

        self.gemini.generate_response.return_value = (
            "Python was created by Guido van Rossum."
        )

        result = self.service.answer(
            user_id=1,
            query="Who created Python?",
            document_id=1,
        )

        self.assertEqual(
            result["answer"],
            "Python was created by Guido van Rossum.",
        )

        self.gemini.generate_response.assert_called_once()

        messages = (
            self.gemini
            .generate_response
            .call_args.args[0]
        )

        prompt = messages[0]["content"]

        self.assertIn(
            "Python was created by Guido van Rossum.",
            prompt,
        )

        self.assertIn(
            "Who created Python?",
            prompt,
        )

    def test_empty_gemini_response_is_rejected(self):

        self.retriever.retrieve.return_value = []

        self.gemini.generate_response.return_value = ""

        with self.assertRaises(
            RuntimeError
        ):
            self.service.answer(
                user_id=1,
                query="What is Python?",
            )

    def test_gemini_failure_is_propagated(self):

        self.retriever.retrieve.return_value = []

        self.gemini.generate_response.side_effect = (
            RuntimeError("Gemini failed")
        )

        with self.assertRaises(
            RuntimeError
        ):
            self.service.answer(
                user_id=1,
                query="What is Python?",
            )