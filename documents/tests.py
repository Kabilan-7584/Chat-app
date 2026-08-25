from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .models import Document


User = get_user_model()


class DocumentModelTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="documentuser",
            password="TestPassword123!",
        )

    def create_document(self):

        uploaded_file = SimpleUploadedFile(
            "test.pdf",
            b"%PDF-test-content",
            content_type="application/pdf",
        )

        return Document.objects.create(
            user=self.user,
            file=uploaded_file,
            filename="test.pdf",
        )

    def test_document_has_correct_owner(self):

        document = self.create_document()

        self.assertEqual(
            document.user,
            self.user,
        )

    def test_document_defaults_to_uploaded_status(self):

        document = self.create_document()

        self.assertEqual(
            document.status,
            Document.ProcessingStatus.UPLOADED,
        )

    def test_document_filename_is_saved(self):

        document = self.create_document()

        self.assertEqual(
            document.filename,
            "test.pdf",
        )

    def test_document_timestamps_are_created(self):

        document = self.create_document()

        self.assertIsNotNone(
            document.created_at,
        )

        self.assertIsNotNone(
            document.updated_at,
        )

    def test_document_status_choices_exist(self):

        self.assertEqual(
            Document.ProcessingStatus.UPLOADED,
            "UPLOADED",
        )

        self.assertEqual(
            Document.ProcessingStatus.PROCESSING,
            "PROCESSING",
        )

        self.assertEqual(
            Document.ProcessingStatus.READY,
            "READY",
        )

        self.assertEqual(
            Document.ProcessingStatus.FAILED,
            "FAILED",
        )

    def test_user_can_have_multiple_documents(self):

        document1 = self.create_document()

        document2_file = SimpleUploadedFile(
            "second.pdf",
            b"%PDF-second-content",
            content_type="application/pdf",
        )

        document2 = Document.objects.create(
            user=self.user,
            file=document2_file,
            filename="second.pdf",
        )

        self.assertEqual(
            Document.objects.filter(
                user=self.user
            ).count(),
            2,
        )

        self.assertEqual(
            document1.user,
            document2.user,
        )
