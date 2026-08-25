from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Document


User = get_user_model()


class DocumentUploadTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="uploaduser",
            password="TestPassword123!",
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            password="TestPassword123!",
        )

    def create_pdf(
        self,
        filename="test.pdf",
        size=100,
    ):

        return SimpleUploadedFile(
            filename,
            b"%PDF-" + (b"x" * size),
            content_type="application/pdf",
        )

    def test_upload_page_requires_login(self):

        response = self.client.get(
            reverse("documents:upload")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_document_list_requires_login(self):

        response = self.client.get(
            reverse("documents:document_list")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_authenticated_user_can_upload_pdf(self):

        self.client.login(
            username="uploaduser",
            password="TestPassword123!",
        )

        response = self.client.post(
            reverse("documents:upload"),
            {
                "file": self.create_pdf(),
            },
        )

        self.assertRedirects(
            response,
            reverse("documents:document_list"),
        )

        document = Document.objects.get(
            user=self.user
        )

        self.assertEqual(
            document.filename,
            "test.pdf",
        )

        self.assertEqual(
            document.status,
            Document.ProcessingStatus.UPLOADED,
        )

    def test_non_pdf_is_rejected(self):

        self.client.login(
            username="uploaduser",
            password="TestPassword123!",
        )

        file = SimpleUploadedFile(
            "test.txt",
            b"not a pdf",
            content_type="text/plain",
        )

        response = self.client.post(
            reverse("documents:upload"),
            {
                "file": file,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            Document.objects.count(),
            0,
        )

    def test_large_file_is_rejected(self):

        self.client.login(
            username="uploaduser",
            password="TestPassword123!",
        )

        large_file = SimpleUploadedFile(
            "large.pdf",
            b"%PDF-" + (
                b"x"
                * (
                    10 * 1024 * 1024
                    + 1
                )
            ),
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse("documents:upload"),
            {
                "file": large_file,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            Document.objects.count(),
            0,
        )

    def test_document_list_only_shows_current_users_documents(self):

        self.client.login(
            username="uploaduser",
            password="TestPassword123!",
        )

        own_file = self.create_pdf(
            filename="own.pdf"
        )

        other_file = self.create_pdf(
            filename="other.pdf"
        )

        Document.objects.create(
            user=self.user,
            file=own_file,
            filename="own.pdf",
        )

        Document.objects.create(
            user=self.other_user,
            file=other_file,
            filename="other.pdf",
        )

        response = self.client.get(
            reverse("documents:document_list")
        )

        self.assertContains(
            response,
            "own.pdf",
        )

        self.assertNotContains(
            response,
            "other.pdf",
        )

    def test_uploaded_document_starts_with_uploaded_status(self):

        self.client.login(
            username="uploaduser",
            password="TestPassword123!",
        )

        self.client.post(
            reverse("documents:upload"),
            {
                "file": self.create_pdf(),
            },
        )

        document = Document.objects.get(
            user=self.user
        )

        self.assertEqual(
            document.status,
            Document.ProcessingStatus.UPLOADED,
        )
