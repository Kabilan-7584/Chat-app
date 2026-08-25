from django.test import SimpleTestCase
from langchain_core.documents import Document

from .services.document_chunking_service import (
    DocumentChunkingService,
)


class DocumentChunkingServiceTests(SimpleTestCase):

    def setUp(self):
        self.service = DocumentChunkingService()

    def test_documents_are_split_into_chunks(self):
        document = Document(
            page_content="A " * 2000,
            metadata={
                "source": "test.pdf",
                "page": 0,
            },
        )

        chunks = self.service.split_documents(
            [document]
        )

        self.assertGreater(
            len(chunks),
            1,
        )

    def test_chunk_size_is_configured(self):
        self.assertEqual(
            self.service.CHUNK_SIZE,
            1000,
        )

    def test_chunk_overlap_is_configured(self):
        self.assertEqual(
            self.service.CHUNK_OVERLAP,
            200,
        )

    def test_metadata_is_preserved(self):
        document = Document(
            page_content="Python " * 300,
            metadata={
                "source": "test.pdf",
                "page": 3,
            },
        )

        chunks = self.service.split_documents(
            [document]
        )

        self.assertGreater(
            len(chunks),
            0,
        )

        for chunk in chunks:
            self.assertEqual(
                chunk.metadata["source"],
                "test.pdf",
            )

            self.assertEqual(
                chunk.metadata["page"],
                3,
            )

    def test_chunk_ids_are_added(self):
        document = Document(
            page_content="Python " * 300,
            metadata={
                "source": "test.pdf",
                "page": 0,
            },
        )

        chunks = self.service.split_documents(
            [document]
        )

        for index, chunk in enumerate(
            chunks,
            start=1,
        ):
            self.assertEqual(
                chunk.metadata["chunk_id"],
                f"chunk-{index}",
            )

    def test_empty_documents_are_rejected(self):
        with self.assertRaises(ValueError):
            self.service.split_documents([])

    def test_none_documents_are_rejected(self):
        with self.assertRaises(ValueError):
            self.service.split_documents(None)
