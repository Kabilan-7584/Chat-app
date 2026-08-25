from unittest import TestCase
from unittest.mock import MagicMock


from documents.services.retriever_service import (
    RetrieverService,
)


class RetrieverServiceTests(TestCase):

    def setUp(self):

        self.embedding_service = (
            MagicMock()
        )

        self.chroma_service = (
            MagicMock()
        )

        self.retriever = RetrieverService(
            embedding_service=(
                self.embedding_service
            ),
            chroma_service=(
                self.chroma_service
            ),
        )

    def test_empty_query_is_rejected(self):

        with self.assertRaises(
            ValueError
        ):
            self.retriever.retrieve(
                user_id=1,
                query="",
            )

    def test_missing_user_is_rejected(self):

        with self.assertRaises(
            ValueError
        ):
            self.retriever.retrieve(
                user_id=None,
                query="Python",
            )

    def test_invalid_top_k_is_rejected(self):

        with self.assertRaises(
            ValueError
        ):
            self.retriever.retrieve(
                user_id=1,
                query="Python",
                top_k=0,
            )

    def test_top_k_limit_is_enforced(self):

        with self.assertRaises(
            ValueError
        ):
            self.retriever.retrieve(
                user_id=1,
                query="Python",
                top_k=21,
            )

    def test_query_embedding_is_generated(self):

        self.embedding_service.embed_query.return_value = [
            0.1,
            0.2,
            0.3,
        ]

        self.chroma_service.collection.query.return_value = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

        self.retriever.retrieve(
            user_id=1,
            query="Who created Python?",
        )

        self.embedding_service.embed_query.assert_called_once_with(
            "Who created Python?"
        )

    def test_results_are_formatted(self):

        self.embedding_service.embed_query.return_value = [
            0.1,
            0.2,
        ]

        self.chroma_service.collection.query.return_value = {
            "ids": [
                ["document-1-chunk-0"]
            ],
            "documents": [
                ["Python was created by Guido."]
            ],
            "metadatas": [
                [
                    {
                        "user_id": "1",
                        "document_id": "1",
                        "filename": "test.pdf",
                        "page_number": 0,
                        "chunk_index": 0,
                    }
                ]
            ],
            "distances": [
                [0.15]
            ],
        }

        results = self.retriever.retrieve(
            user_id=1,
            query="Who created Python?",
        )

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0]["id"],
            "document-1-chunk-0",
        )

        self.assertEqual(
            results[0]["content"],
            "Python was created by Guido.",
        )

    def test_document_filter_is_applied(self):

        self.embedding_service.embed_query.return_value = [
            0.1,
            0.2,
        ]

        self.chroma_service.collection.query.return_value = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

        self.retriever.retrieve(
            user_id=7,
            query="Python",
            document_id=25,
            top_k=3,
        )

        call_kwargs = (
            self.chroma_service
            .collection
            .query.call_args.kwargs
        )

        self.assertEqual(
            call_kwargs["n_results"],
            3,
        )

        self.assertEqual(
            call_kwargs["where"],
            {
                "$and": [
                    {"user_id": "7"},
                    {"document_id": "25"},
                ]
            },
        )