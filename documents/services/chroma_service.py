from pathlib import Path

import chromadb
from django.conf import settings


class ChromaService:
    """
    Service responsible for storing document chunks
    and their embeddings in ChromaDB.

    This service does NOT perform:
    - retrieval
    - similarity search
    - RAG
    """

    COLLECTION_NAME = "document_chunks"

    def __init__(self):

        persist_directory = (
            Path(settings.BASE_DIR)
            / "chroma_db"
        )

        persist_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.client = (
            chromadb.PersistentClient(
                path=str(persist_directory)
            )
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=self.COLLECTION_NAME
            )
        )

    @staticmethod
    def build_chunk_id(
        document_id,
        chunk_index,
    ):
        """
        Build a stable Chroma record ID.
        """

        return (
            f"document-{document_id}"
            f"-chunk-{chunk_index}"
        )

    def add_chunks(
        self,
        *,
        user_id,
        document_id,
        filename,
        chunks,
        embeddings,
    ):
        """
        Store document chunks and embeddings.
        """

        if not chunks:
            raise ValueError(
                "Chunks cannot be empty."
            )

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Chunks and embeddings must have "
                "the same length."
            )

        ids = []
        documents = []
        metadatas = []

        for index, (
            chunk,
            embedding,
        ) in enumerate(
            zip(chunks, embeddings)
        ):

            chunk_id = self.build_chunk_id(
                document_id,
                index,
            )

            ids.append(chunk_id)

            documents.append(
                chunk.page_content
            )

            metadatas.append(
                {
                    "user_id": str(user_id),
                    "document_id": str(
                        document_id
                    ),
                    "filename": filename,
                    "page_number": int(
                        chunk.metadata.get(
                            "page",
                            0,
                        )
                    ),
                    "chunk_index": index,
                }
            )

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return ids

    def delete_document(
        self,
        *,
        user_id,
        document_id,
    ):
        """
        Delete all chunks belonging to a document
        owned by the specified user.
        """

        results = self.collection.get(
            where={
                "$and": [
                    {
                        "user_id": str(
                            user_id
                        )
                    },
                    {
                        "document_id": str(
                            document_id
                        )
                    },
                ]
            },
            include=[],
        )

        ids = results.get("ids", [])

        if ids:
            self.collection.delete(
                ids=ids
            )

        return len(ids)

    def count(self):
        """
        Return the number of stored chunks.
        """

        return self.collection.count()