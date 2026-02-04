"""
Models for notes and categories.
"""

import uuid

from django.conf import settings
from django.core.validators import MaxLengthValidator, RegexValidator
from django.db import models


class Category(models.Model):
    """
    Category model for organizing notes.

    Each user has their own isolated set of categories.
    Category names are unique within a user's scope, not globally.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
        db_index=True,
        help_text="Owner of this category",
    )
    name = models.CharField(
        max_length=100,
        help_text="Category name (unique per user)",
    )
    color = models.CharField(
        max_length=7,
        default="#6366f1",
        validators=[
            RegexValidator(
                regex=r"^#[0-9A-Fa-f]{6}$",
                message="Color must be a valid hex color code (e.g., #6366f1)",
            )
        ],
        help_text="Hex color code for UI display",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categories"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["created_at"]
        # Composite unique constraint: category names are unique per user
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_category_name_per_user",
            )
        ]
        indexes = [
            models.Index(fields=["user"], name="idx_category_user"),
            models.Index(fields=["user", "name"], name="idx_category_user_name"),
        ]

    def __str__(self):
        return f"{self.name} ({self.user.email})"


class Note(models.Model):
    """
    Note model for storing user notes.

    Uses UUID primary keys to prevent ID enumeration attacks.
    Notes can optionally be organized into categories.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="UUID primary key for security",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes",
        db_index=True,
        help_text="Owner of this note",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notes",
        db_index=True,
        help_text="Category this note belongs to (optional)",
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Note title",
    )
    content = models.TextField(
        blank=True,
        validators=[MaxLengthValidator(100000)],
        help_text="Note content (max 100,000 characters)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(
        auto_now=True,
        db_index=True,
        help_text="Last update timestamp (used for sorting recent notes)",
    )

    class Meta:
        db_table = "notes"
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user"], name="idx_note_user"),
            models.Index(
                fields=["user", "-updated_at"], name="idx_note_user_updated"
            ),
            models.Index(fields=["category"], name="idx_note_category"),
            models.Index(fields=["title"], name="idx_note_title"),
            models.Index(fields=["-updated_at"], name="idx_note_updated"),
        ]

    def __str__(self):
        title_preview = self.title[:50] if self.title else "(Untitled)"
        return f"{title_preview} - {self.user.email}"
