from django import forms

from .models import Document


class DocumentUploadForm(forms.ModelForm):

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    class Meta:
        model = Document

        fields = [
            "file",
        ]

        widgets = {
            "file": forms.ClearableFileInput(
                attrs={
                    "accept": ".pdf,application/pdf",
                }
            ),
        }

    def clean_file(self):

        uploaded_file = self.cleaned_data.get("file")

        if not uploaded_file:
            raise forms.ValidationError(
                "Please select a PDF file."
            )

        filename = uploaded_file.name or ""

        if not filename.lower().endswith(".pdf"):
            raise forms.ValidationError(
                "Only PDF files are allowed."
            )

        if uploaded_file.size > self.MAX_FILE_SIZE:
            raise forms.ValidationError(
                "PDF file size cannot exceed 10 MB."
            )

        content_type = (
            uploaded_file.content_type or ""
        ).lower()

        if content_type not in (
            "application/pdf",
            "application/x-pdf",
            "",
        ):
            raise forms.ValidationError(
                "The uploaded file must be a PDF."
            )

        return uploaded_file
