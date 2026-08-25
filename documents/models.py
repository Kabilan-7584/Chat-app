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
