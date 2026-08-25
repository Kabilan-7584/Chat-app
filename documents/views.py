from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import DocumentUploadForm
from .models import Document


@login_required
def document_list(request):

    documents = (
        Document.objects
        .filter(user=request.user)
        .order_by("-updated_at")
    )

    return render(
        request,
        "documents/document_list.html",
        {
            "documents": documents,
        },
    )


@login_required
def upload_document(request):

    if request.method == "POST":

        form = DocumentUploadForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            document = form.save(
                commit=False
            )

            document.user = request.user

            document.filename = (
                document.file.name
            )

            document.status = (
                Document.ProcessingStatus.UPLOADED
            )

            document.save()

            return redirect(
                "documents:document_list"
            )

    else:

        form = DocumentUploadForm()

    return render(
        request,
        "documents/upload.html",
        {
            "form": form,
        },
    )
