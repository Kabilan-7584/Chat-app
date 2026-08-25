from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)


class DocumentChunkingService:
    """
    Split extracted LangChain Documents into
    smaller chunks.

    This service does NOT perform:
    - embeddings
    - vector storage
    - retrieval
    - RAG
    """

    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

    def __init__(self):

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.CHUNK_SIZE,
            chunk_overlap=self.CHUNK_OVERLAP,
            separators=[
                "\n\n",
                "\n",
                " ",
                "",
            ],
            length_function=len,
        )

    def split_documents(self, documents):

        if documents is None:
            raise ValueError(
                "Documents are required."
            )

        if not documents:
            raise ValueError(
                "Documents cannot be empty."
            )

        chunks = self.splitter.split_documents(
            documents
        )

        if not chunks:
            raise RuntimeError(
                "Document chunking produced no chunks."
            )

        for index, chunk in enumerate(
            chunks,
            start=1,
        ):
            chunk.metadata = {
                **chunk.metadata,
                "chunk_id": f"chunk-{index}",
            }

        return chunks
