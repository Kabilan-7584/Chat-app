from unittest import TestCase

from documents.services.chroma_service import ChromaService


class ChromaServiceTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.service = ChromaService()

    def test_collection_exists(self):

        self.assertEqual(
            self.service.collection.name,
            ChromaService.COLLECTION_NAME,
        )

    def test_build_chunk_id(self):

        chunk_id = (
            self.service.build_chunk_id(
                10,
                5,
            )
        )

        self.assertEqual(
            chunk_id,
            "document-10-chunk-5",
        )

    def test_empty_chunks_are_rejected(self):

        with self.assertRaises(ValueError):

            self.service.add_chunks(
                user_id=1,
                document_id=1,
                filename="test.pdf",
                chunks=[],
                embeddings=[],
            )

    def test_mismatched_embeddings_are_rejected(self):

        with self.assertRaises(ValueError):

            self.service.add_chunks(
                user_id=1,
                document_id=1,
                filename="test.pdf",
                chunks=[object()],
                embeddings=[],
            )