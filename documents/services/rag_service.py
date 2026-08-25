from documents.services.retriever_service import (
    RetrieverService,
)
from ai.services.gemini_service import GeminiService


class RAGService:
    """
    Retrieval-Augmented Generation service.

    Flow:

    Question
        ↓
    Retriever
        ↓
    Relevant chunks
        ↓
    Context
        ↓
    Gemini
        ↓
    Grounded answer
    """

    DEFAULT_TOP_K = 5

    def __init__(
        self,
        retriever_service=None,
        gemini_service=None,
    ):
        self.retriever = (
            retriever_service
            or RetrieverService()
        )

        self.gemini = (
            gemini_service
            or GeminiService()
        )

    def answer(
        self,
        *,
        user_id,
        query,
        document_id=None,
        top_k=DEFAULT_TOP_K,
    ):
        """
        Generate an answer grounded in retrieved
        document context.
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

        results = self.retriever.retrieve(
            user_id=user_id,
            query=query,
            document_id=document_id,
            top_k=top_k,
        )

        context = self._build_context(
            results
        )

        prompt = self._build_prompt(
            query=query,
            context=context,
        )

        response = self.gemini.generate_response(
            [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )

        if not response or not response.strip():
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return {
            "answer": response.strip(),
            "sources": results,
        }

    @staticmethod
    def _build_context(results):
        """
        Convert retrieved chunks into a context
        block for Gemini.
        """

        if not results:
            return (
                "No relevant information was "
                "retrieved from the documents."
            )

        context_parts = []

        for index, result in enumerate(
            results,
            start=1,
        ):
            metadata = result["metadata"]

            context_parts.append(
                (
                    f"[SOURCE {index}]\n"
                    f"Filename: "
                    f"{metadata.get('filename')}\n"
                    f"Page: "
                    f"{metadata.get('page_number')}\n"
                    f"Content:\n"
                    f"{result['content']}"
                )
            )

        return "\n\n".join(
            context_parts
        )

    @staticmethod
    def _build_prompt(
        *,
        query,
        context,
    ):
        """
        Build a grounding-focused prompt.
        """

        return f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the
information contained in the provided document
context.

GROUNDING RULES:

1. Use the provided context as the source of truth.
2. Do not invent or assume information that is
   not present in the context.
3. Do not use outside knowledge to fill missing
   information.
4. If the context does not contain enough
   information to answer the question, clearly
   state that the answer is not supported by
   the provided documents.
5. Keep the answer concise and directly related
   to the question.

DOCUMENT CONTEXT:

{context}

USER QUESTION:

{query}

ANSWER:
""".strip()