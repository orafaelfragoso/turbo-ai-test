"""
Django app configuration for notes app.
"""

from django.apps import AppConfig


class NotesConfig(AppConfig):
    """
    Configuration for the notes app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notes"
    verbose_name = "Notes"
