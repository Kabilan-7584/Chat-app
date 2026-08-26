from django.conf import settings
from django.db import models


class Document(models.Model):

    class ProcessingStatus(models.TextChoices):
        UPLOADED = "UPLOADED", "Uploaded"
        PROCESSING = "PROCESSING", "Processing"
        READY = "READY", "Ready"
        FAILED = "FAILED", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    file = models.FileField(
        upload_to="documents/",
    )

    filename = models.CharField(
        max_length=255,
    )

    status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.UPLOADED,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-updated_at"]

        indexes = [
            models.Index(
                fields=["user", "-updated_at"],
            ),
            models.Index(
                fields=["user", "status"],
            ),
        ]

    def __str__(self):
        return self.filename


class DocumentConversation(models.Model):
    """
    Conversation associated with one document
    and one authenticated user.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="document_conversations",
    )

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="conversations",
    )

    title = models.CharField(
        max_length=255,
        default="New Conversation",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-updated_at"]

        indexes = [
            models.Index(
                fields=["user", "-updated_at"],
            ),
            models.Index(
                fields=["document", "-updated_at"],
            ),
        ]

    def __str__(self):
        return self.title


class DocumentMessage(models.Model):
    """
    Message belonging to a document conversation.
    """

    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"

    conversation = models.ForeignKey(
        DocumentConversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["created_at"]

        indexes = [
            models.Index(
                fields=["conversation", "created_at"],
            ),
        ]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"