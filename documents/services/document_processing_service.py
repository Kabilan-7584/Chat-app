from django.db import transaction

from documents.models import Document

from .pdf_extraction_service import PDFExtractionService


class DocumentProcessingService:
    """
    Coordinates document processing.

    Phase 14 only performs PDF text extraction.
    """

    def __init__(self):

        self.pdf_service = (
            PDFExtractionService()
        )

    @transaction.atomic
    def process(self, document):
        """
        Process a Document record.

        Status lifecycle:

        UPLOADED
            ?
        PROCESSING
            ?
        READY

        Failure:

        PROCESSING
            ?
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

            documents = (
                self.pdf_service.extract(
                    document.file.path
                )
            )

            if not documents:

                raise RuntimeError(
                    "No PDF pages were extracted."
                )

            document.status = (
                Document.ProcessingStatus.READY
            )

            document.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            return documents

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
