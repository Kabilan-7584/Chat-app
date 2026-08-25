from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):

    list_display = (
        "filename",
        "user",
        "status",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "filename",
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-updated_at",
    )
