"""
Django admin configuration for notes app.
"""

from django.contrib import admin

from .models import Category, Note


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for Category model.
    """

    list_display = ("id", "name", "user", "color", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "user__email")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("id", "user", "name", "color")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """
    Admin interface for Note model.
    """

    list_display = ("id", "title", "user", "category", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at", "category")
    search_fields = ("title", "content", "user__email")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-updated_at",)

    fieldsets = (
        (None, {"fields": ("id", "user", "category", "title")}),
        ("Content", {"fields": ("content",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
