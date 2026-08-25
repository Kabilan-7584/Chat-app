from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Service responsible for converting text into vector embeddings.
    """

    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self):
        self.model = SentenceTransformer(
            self.MODEL_NAME
        )

    def embed_text(self, text: str) -> list[float]:
        """
        Convert a single text into an embedding vector.
        """

        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                "Text cannot be empty."
            )

        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
        )

        return embedding.tolist()

    def embed_documents(
        self,
        documents,
    ) -> list[list[float]]:
        """
        Convert multiple document chunks into embeddings.
        """

        if not documents:
            return []

        texts = [
            document.page_content
            for document in documents
        ]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
        )

        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        """
        Convert a user query into an embedding vector.
        """

        return self.embed_text(query)

    def get_embedding_dimension(self) -> int:
        """
        Return the dimensionality of the embedding model.
        """

        return self.model.get_sentence_embedding_dimension()