from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader


class PDFExtractionService:
    """
    Extract text and metadata from PDF files.

    This service does NOT perform:
    - chunking
    - embeddings
    - vector storage
    - retrieval
    - RAG
    """

    def extract(self, file_path):
        """
        Load a PDF and return LangChain Document objects.
        """

        if not file_path:
            raise ValueError(
                "PDF file path is required."
            )

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                "PDF file does not exist."
            )

        if not path.is_file():
            raise ValueError(
                "PDF path must point to a file."
            )

        try:

            loader = PyPDFLoader(
                str(path)
            )

            documents = loader.load()

        except Exception as exc:

            raise RuntimeError(
                "PDF extraction failed."
            ) from exc

        if not documents:

            raise RuntimeError(
                "PDF contains no extractable pages."
            )

        return documents
