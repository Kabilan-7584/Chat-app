from documents.services.retriever_service import (
    RetrieverService,
)

from ai.services.gemini_service import (
    GeminiService,
)


class RAGService:
    """
    Retrieval-Augmented Generation service.

    Flow:

    User Question
        ↓
    Retriever
        ↓
    Relevant Chunks
        ↓
    Context
        ↓
    Conversation History
        ↓
    Grounded Prompt
        ↓
    Gemini
        ↓
    Answer + Sources
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
        conversation_history=None,
        top_k=DEFAULT_TOP_K,
    ):
        """
        Retrieve relevant document chunks and
        generate a grounded answer using Gemini.

        Conversation history is used to understand
        follow-up questions.
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

        if conversation_history is None:
            conversation_history = []

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
            conversation_history=(
                conversation_history
            ),
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
            "sources": self._build_sources(
                results
            ),
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
            metadata = result.get(
                "metadata",
                {},
            )

            context_parts.append(
                (
                    f"[SOURCE {index}]\n"
                    f"Filename: "
                    f"{metadata.get('filename')}\n"
                    f"Page: "
                    f"{metadata.get('page_number')}\n"
                    f"Content:\n"
                    f"{result.get('content', '')}"
                )
            )

        return "\n\n".join(
            context_parts
        )

    @staticmethod
    def _build_sources(results):
        """
        Convert retrieved chunk metadata into
        user-facing source references.
        """

        sources = []

        for result in results:
            metadata = result.get(
                "metadata",
                {},
            )

            sources.append(
                {
                    "document_id": metadata.get(
                        "document_id"
                    ),
                    "filename": metadata.get(
                        "filename"
                    ),
                    "page_number": metadata.get(
                        "page_number"
                    ),
                    "chunk_id": result.get(
                        "id"
                    ),
                }
            )

        return sources

    @staticmethod
    def _build_conversation_history(
        conversation_history,
    ):
        """
        Convert stored conversation messages
        into readable prompt context.
        """

        if not conversation_history:
            return "No previous conversation."

        history_parts = []

        for message in conversation_history:
            role = message.get(
                "role",
                "",
            )

            content = message.get(
                "content",
                "",
            )

            history_parts.append(
                f"{role.upper()}: {content}"
            )

        return "\n".join(
            history_parts
        )

    @classmethod
    def _build_prompt(
        cls,
        *,
        query,
        context,
        conversation_history=None,
    ):
        """
        Build a grounding-focused prompt with
        optional previous conversation context.

        conversation_history is optional so that
        single-turn RAG requests and existing tests
        continue to work.
        """

        history = (
            cls._build_conversation_history(
                conversation_history
            )
        )

        return f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the
information contained in the provided document
context.

Use previous conversation only to understand
follow-up questions and references such as
"it", "they", "that", or "this".

GROUNDING RULES:

1. Use the provided document context as the
   source of truth.
2. Do not invent information.
3. Do not use outside knowledge to fill gaps.
4. If the answer is not supported by the
   document context, clearly state that the
   answer is not supported by the provided
   documents.
5. Previous conversation must not override
   the document context.
6. Keep the answer concise and relevant.

PREVIOUS CONVERSATION:

{history}

DOCUMENT CONTEXT:

{context}

CURRENT USER QUESTION:

{query}

ANSWER:
""".strip()