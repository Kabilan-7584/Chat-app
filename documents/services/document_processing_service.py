from django.db import transaction

from documents.models import Document

from .chroma_service import ChromaService
from .document_chunking_service import (
    DocumentChunkingService,
)
from .embedding_service import EmbeddingService
from .pdf_extraction_service import (
    PDFExtractionService,
)


class DocumentProcessingService:
    """
    Coordinates the complete document processing pipeline.

    Pipeline:

    PDF
        ↓
    Extraction
        ↓
    Chunking
        ↓
    Embeddings
        ↓
    ChromaDB
        ↓
    READY
    """

    def __init__(self):
        self.pdf_service = (
            PDFExtractionService()
        )

        self.chunking_service = (
            DocumentChunkingService()
        )

        self.embedding_service = (
            EmbeddingService()
        )

        self.chroma_service = (
            ChromaService()
        )

    @transaction.atomic
    def process(self, document):
        """
        Process an uploaded document.

        Status lifecycle:

        UPLOADED
            ↓
        PROCESSING
            ↓
        READY

        Failure:

        PROCESSING
            ↓
        FAILED
        """

        if not document.file:
            raise ValueError(
                "Document does not have a file."
            )

        document.status = (
            Document.ProcessingStatus.PROCESSING
        )

        document.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        try:

            # -------------------------------------------------
            # STEP 1 — PDF EXTRACTION
            # -------------------------------------------------

            documents = (
                self.pdf_service.extract(
                    document.file.path
                )
            )

            if not documents:
                raise RuntimeError(
                    "No PDF pages were extracted."
                )

            # -------------------------------------------------
            # STEP 2 — CHUNKING
            # -------------------------------------------------

            chunks = (
                self.chunking_service
                .split_documents(
                    documents
                )
            )

            if not chunks:
                raise RuntimeError(
                    "Document chunking produced no chunks."
                )

            # -------------------------------------------------
            # STEP 3 — EMBEDDINGS
            # -------------------------------------------------

            embeddings = (
                self.embedding_service
                .embed_documents(
                    chunks
                )
            )

            if not embeddings:
                raise RuntimeError(
                    "Embedding generation produced no vectors."
                )

            if len(embeddings) != len(chunks):
                raise RuntimeError(
                    "Number of embeddings does not "
                    "match number of chunks."
                )

            # -------------------------------------------------
            # STEP 4 — CHROMADB STORAGE
            # -------------------------------------------------

            self.chroma_service.add_chunks(
                user_id=document.user_id,
                document_id=document.id,
                filename=document.filename,
                chunks=chunks,
                embeddings=embeddings,
            )

            # -------------------------------------------------
            # STEP 5 — MARK READY
            # -------------------------------------------------

            document.status = (
                Document.ProcessingStatus.READY
            )

            document.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            return chunks

        except Exception as exc:

            document.status = (
                Document.ProcessingStatus.FAILED
            )

            document.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            raise RuntimeError(
                "Document processing failed."
            ) from exc