from documents.services.chroma_service import ChromaService
from documents.services.embedding_service import EmbeddingService


class RetrieverService:
    """
    Perform semantic retrieval against ChromaDB.

    This service does NOT:
    - generate answers
    - call Gemini
    - perform RAG
    """

    DEFAULT_TOP_K = 5
    MAX_TOP_K = 20

    def __init__(
        self,
        embedding_service=None,
        chroma_service=None,
    ):
        self.embedding_service = (
            embedding_service
            or EmbeddingService()
        )

        self.chroma_service = (
            chroma_service
            or ChromaService()
        )

    def retrieve(
        self,
        *,
        user_id,
        query,
        document_id=None,
        top_k=DEFAULT_TOP_K,
    ):
        """
        Retrieve the most semantically relevant
        chunks belonging to the specified user.
        """

        if user_id is None:
            raise ValueError(
                "User ID is required."
            )

        if not isinstance(query, str):
            raise ValueError(
                "Query must be a string."
            )

        query = query.strip()

        if not query:
            raise ValueError(
                "Query cannot be empty."
            )

        if not isinstance(top_k, int):
            raise ValueError(
                "top_k must be an integer."
            )

        if top_k < 1:
            raise ValueError(
                "top_k must be greater than zero."
            )

        if top_k > self.MAX_TOP_K:
            raise ValueError(
                f"top_k cannot exceed "
                f"{self.MAX_TOP_K}."
            )

        query_embedding = (
            self.embedding_service.embed_query(
                query
            )
        )

        where_filters = [
            {
                "user_id": str(user_id)
            }
        ]

        if document_id is not None:
            where_filters.append(
                {
                    "document_id": str(
                        document_id
                    )
                }
            )

        if len(where_filters) == 1:
            where = where_filters[0]
        else:
            where = {
                "$and": where_filters
            }

        results = (
            self.chroma_service.collection.query(
                query_embeddings=[
                    query_embedding
                ],
                n_results=top_k,
                where=where,
                include=[
                    "documents",
                    "metadatas",
                    "distances",
                ],
            )
        )

        return self._format_results(
            results
        )

    @staticmethod
    def _format_results(results):
        """
        Convert Chroma's nested query response
        into a simpler result structure.
        """

        ids = (
            results.get("ids", [[]])[0]
        )

        documents = (
            results.get(
                "documents",
                [[]],
            )[0]
        )

        metadatas = (
            results.get(
                "metadatas",
                [[]],
            )[0]
        )

        distances = (
            results.get(
                "distances",
                [[]],
            )[0]
        )

        formatted = []

        for index, chunk_id in enumerate(
            ids
        ):

            formatted.append(
                {
                    "id": chunk_id,
                    "content": documents[index],
                    "metadata": metadatas[index],
                    "distance": distances[index],
                }
            )

        return formatted
    