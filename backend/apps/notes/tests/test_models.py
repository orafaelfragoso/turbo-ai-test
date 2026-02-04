"""
Tests for notes and categories models.
"""

import uuid

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError

from apps.notes.models import Category, Note

User = get_user_model()


@pytest.mark.django_db
class TestCategoryModel:
    """Tests for Category model."""

    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(email="test@example.com", password="testpass123")

    @pytest.fixture
    def category(self, user):
        """Create a test category."""
        return Category.objects.create(user=user, name="Test Category", color="#6366f1")

    def test_create_category(self, user):
        """Test creating a category."""
        category = Category.objects.create(
            user=user, name="My Category", color="#10b981"
        )

        assert category.id is not None
        assert category.user == user
        assert category.name == "My Category"
        assert category.color == "#10b981"
        assert category.created_at is not None
        assert category.updated_at is not None

    def test_category_default_color(self, user):
        """Test category default color."""
        category = Category.objects.create(user=user, name="Test")

        assert category.color == "#6366f1"

    def test_category_unique_name_per_user(self, user):
        """Test category name uniqueness is per user, not global."""
        from django.db import transaction

        # Create first category
        Category.objects.create(user=user, name="Work")

        # Creating another category with same name for same user should fail
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Category.objects.create(user=user, name="Work")

        # But creating a category with same name for different user should succeed
        user2 = User.objects.create_user(email="user2@example.com", password="pass123")
        category2 = Category.objects.create(user=user2, name="Work")

        assert category2.name == "Work"
        assert category2.user == user2

    def test_category_invalid_color(self, user):
        """Test category with invalid hex color."""
        category = Category(user=user, name="Test", color="invalid")

        with pytest.raises(DjangoValidationError):
            category.full_clean()

    def test_category_valid_hex_color(self, user):
        """Test category with valid hex colors."""
        valid_colors = ["#000000", "#FFFFFF", "#6366f1", "#10b981", "#f59e0b"]

        for color in valid_colors:
            category = Category(user=user, name=f"Test {color}", color=color)
            category.full_clean()  # Should not raise

    def test_category_str_representation(self, category):
        """Test category string representation."""
        assert str(category) == "Test Category (test@example.com)"

    def test_category_ordering(self, user):
        """Test categories are ordered by created_at."""
        cat1 = Category.objects.create(user=user, name="First")
        cat2 = Category.objects.create(user=user, name="Second")
        cat3 = Category.objects.create(user=user, name="Third")

        categories = list(Category.objects.filter(user=user))

        assert categories[0] == cat1
        assert categories[1] == cat2
        assert categories[2] == cat3

    def test_category_cascade_delete_user(self, user, category):
        """Test category is deleted when user is deleted."""
        category_id = category.id
        user.delete()

        assert not Category.objects.filter(id=category_id).exists()


@pytest.mark.django_db
class TestNoteModel:
    """Tests for Note model."""

    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(email="test@example.com", password="testpass123")

    @pytest.fixture
    def category(self, user):
        """Create a test category."""
        return Category.objects.create(user=user, name="Test Category")

    @pytest.fixture
    def note(self, user, category):
        """Create a test note."""
        return Note.objects.create(
            user=user,
            category=category,
            title="Test Note",
            content="Test content",
        )

    def test_create_note(self, user, category):
        """Test creating a note."""
        note = Note.objects.create(
            user=user,
            category=category,
            title="My Note",
            content="My content",
        )

        assert isinstance(note.id, uuid.UUID)
        assert note.user == user
        assert note.category == category
        assert note.title == "My Note"
        assert note.content == "My content"
        assert note.created_at is not None
        assert note.updated_at is not None

    def test_note_uuid_primary_key(self, user):
        """Test note uses UUID as primary key."""
        note = Note.objects.create(user=user, title="Test")

        assert isinstance(note.id, uuid.UUID)
        assert note.id != uuid.UUID(int=0)

    def test_note_blank_title_and_content(self, user):
        """Test note can have blank title and content."""
        note = Note.objects.create(user=user, title="", content="")

        assert note.title == ""
        assert note.content == ""

    def test_note_without_category(self, user):
        """Test note can exist without a category."""
        note = Note.objects.create(user=user, title="Uncategorized", content="Test")

        assert note.category is None

    def test_note_set_null_on_category_delete(self, user, category):
        """Test note's category is set to NULL when category is deleted."""
        note = Note.objects.create(user=user, category=category, title="Test")

        assert note.category == category

        category.delete()
        note.refresh_from_db()

        assert note.category is None

    def test_note_max_content_length(self, user):
        """Test note content max length validation."""
        # Content exactly at limit should be OK
        content_at_limit = "x" * 100000
        note = Note(user=user, title="Test", content=content_at_limit)
        note.full_clean()  # Should not raise

        # Content over limit should fail
        content_over_limit = "x" * 100001
        note_over = Note(user=user, title="Test", content=content_over_limit)

        with pytest.raises(DjangoValidationError):
            note_over.full_clean()

    def test_note_str_representation(self, note):
        """Test note string representation."""
        assert str(note) == "Test Note - test@example.com"

    def test_note_str_untitled(self, user):
        """Test note string representation for untitled notes."""
        note = Note.objects.create(user=user, title="", content="Test")

        assert "(Untitled)" in str(note)

    def test_note_str_long_title(self, user):
        """Test note string representation truncates long titles."""
        long_title = "x" * 100
        note = Note.objects.create(user=user, title=long_title, content="Test")

        # String representation should truncate to 50 characters
        assert len(str(note).split(" - ")[0]) <= 50

    def test_note_ordering(self, user):
        """Test notes are ordered by updated_at descending."""
        note1 = Note.objects.create(user=user, title="First")
        note2 = Note.objects.create(user=user, title="Second")
        note3 = Note.objects.create(user=user, title="Third")

        notes = list(Note.objects.filter(user=user))

        # Should be in reverse order (most recently updated first)
        assert notes[0] == note3
        assert notes[1] == note2
        assert notes[2] == note1

    def test_note_cascade_delete_user(self, user, note):
        """Test note is deleted when user is deleted."""
        note_id = note.id
        user.delete()

        assert not Note.objects.filter(id=note_id).exists()

    def test_note_auto_updated_at(self, note):
        """Test note's updated_at is automatically updated on save."""
        original_updated_at = note.updated_at

        # Update note
        note.title = "Updated Title"
        note.save()

        # updated_at should be newer
        assert note.updated_at > original_updated_at
