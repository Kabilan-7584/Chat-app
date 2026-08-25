from unittest import TestCase
from unittest.mock import patch

from documents.services.embedding_service import EmbeddingService


class EmbeddingServiceTests(TestCase):

    def setUp(self):
        self.service = EmbeddingService.__new__(
            EmbeddingService
        )

    def test_empty_text_is_rejected(self):

        with self.assertRaises(ValueError):
            self.service.embed_text("")

    def test_whitespace_text_is_rejected(self):

        with self.assertRaises(ValueError):
            self.service.embed_text("   ")

    @patch(
        "documents.services.embedding_service.SentenceTransformer"
    )
    def test_embedding_dimension(
        self,
        mock_model,
    ):

        mock_instance = mock_model.return_value

        mock_instance.get_sentence_embedding_dimension.return_value = 384

        service = EmbeddingService()

        self.assertEqual(
            service.get_embedding_dimension(),
            384,
        )
        