"""
Tests for notes and categories serializers.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache

from apps.notes.models import Category, Note
from apps.notes.serializers import (
    CategoryListSerializer,
    CategoryNestedSerializer,
    CategorySerializer,
    NoteCreateSerializer,
    NoteDetailSerializer,
    NoteListSerializer,
    NoteUpdateSerializer,
)

User = get_user_model()


@pytest.mark.django_db
class TestCategorySerializer:
    """Tests for CategorySerializer."""

    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(email="test@example.com", password="testpass123")

    def test_valid_category_data(self):
        """Test serializer with valid category data."""
        data = {"name": "Work", "color": "#10b981"}
        serializer = CategorySerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["name"] == "Work"
        assert serializer.validated_data["color"] == "#10B981"  # Uppercase

    def test_category_default_color(self):
        """Test serializer uses default color if not provided."""
        data = {"name": "Work"}
        serializer = CategorySerializer(data=data)

        assert serializer.is_valid()

    def test_category_empty_name(self):
        """Test serializer rejects empty name."""
        data = {"name": ""}
        serializer = CategorySerializer(data=data)

        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_category_whitespace_name(self):
        """Test serializer rejects whitespace-only name."""
        data = {"name": "   "}
        serializer = CategorySerializer(data=data)

        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_category_invalid_color_format(self):
        """Test serializer rejects invalid color format."""
        invalid_colors = ["invalid", "123456", "#GGG", "#12345", "#1234567"]

        for color in invalid_colors:
            data = {"name": "Test", "color": color}
            serializer = CategorySerializer(data=data)

            assert not serializer.is_valid(), f"Color {color} should be invalid"
            assert "color" in serializer.errors

    def test_category_valid_color_formats(self):
        """Test serializer accepts valid color formats."""
        valid_colors = ["#000000", "#ffffff", "#6366f1", "#10b981"]

        for color in valid_colors:
            data = {"name": "Test", "color": color}
            serializer = CategorySerializer(data=data)

            assert serializer.is_valid(), f"Color {color} should be valid"

    def test_category_name_stripped(self):
        """Test serializer strips whitespace from name."""
        data = {"name": "  Work  ", "color": "#10b981"}
        serializer = CategorySerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["name"] == "Work"


@pytest.mark.django_db
class TestCategoryListSerializer:
    """Tests for CategoryListSerializer."""

    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(email="test@example.com", password="testpass123")

    @pytest.fixture
    def category(self, user):
        """Create a test category."""
        return Category.objects.create(user=user, name="Test Category")

    def test_category_list_serializer_includes_note_count(self, category):
        """Test serializer includes note_count field."""
        from django.core.cache import cache

        # Clear cache to ensure we're testing fresh
        cache_key = f"category:{category.id}:note_count"
        cache.delete(cache_key)

        # Create some notes
        Note.objects.create(user=category.user, category=category, title="Note 1")
        Note.objects.create(user=category.user, category=category, title="Note 2")

        serializer = CategoryListSerializer(category)

        assert "note_count" in serializer.data
        assert serializer.data["note_count"] == 2

    def test_category_list_serializer_caches_note_count(self, category):
        """Test serializer caches note count in Redis."""
        cache_key = f"category:{category.id}:note_count"
        cache.delete(cache_key)  # Ensure cache is empty

        # First call should query database and cache result
        serializer = CategoryListSerializer(category)
        note_count = serializer.data["note_count"]

        # Cache should now be populated
        cached_count = cache.get(cache_key)
        assert cached_count == note_count

    def test_category_list_serializer_uses_cache(self, category):
        """Test serializer uses cached note count."""
        cache_key = f"category:{category.id}:note_count"

        # Set cache to a specific value
        cache.set(cache_key, 42, timeout=3600)

        serializer = CategoryListSerializer(category)

        # Should return cached value, not database count
        assert serializer.data["note_count"] == 42


@pytest.mark.django_db
class TestCategoryNestedSerializer:
    """Tests for CategoryNestedSerializer."""

    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(email="test@example.com", password="testpass123")

    @pytest.fixture
    def category(self, user):
        """Create a test category."""
        return Category.objects.create(user=user, name="Test Category", color="#6366f1")

    def test_category_nested_serializer_fields(self, category):
        """Test nested serializer only includes id, name, and color."""
        serializer = CategoryNestedSerializer(category)

        assert set(serializer.data.keys()) == {"id", "name", "color"}
        assert serializer.data["id"] == category.id
        assert serializer.data["name"] == "Test Category"
        assert serializer.data["color"] == "#6366f1"


@pytest.mark.django_db
class TestNoteCreateSerializer:
    """Tests for NoteCreateSerializer."""

    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(email="test@example.com", password="testpass123")

    @pytest.fixture
    def category(self, user):
        """Create a test category."""
        return Category.objects.create(user=user, name="Test Category")

    def test_valid_note_data(self, user, category):
        """Test serializer with valid note data."""
        data = {"title": "My Note", "content": "My content", "category_id": category.id}
        serializer = NoteCreateSerializer(data=data, context={"user": user})

        assert serializer.is_valid()
        assert serializer.validated_data["title"] == "My Note"
        assert serializer.validated_data["content"] == "My content"
        assert serializer.validated_data["category_id"] == category.id

    def test_note_optional_fields(self, user):
        """Test serializer with optional fields omitted."""
        data = {}
        serializer = NoteCreateSerializer(data=data, context={"user": user})

        assert serializer.is_valid()

    def test_note_blank_title_and_content(self, user):
        """Test serializer accepts blank title and content."""
        data = {"title": "", "content": ""}
        serializer = NoteCreateSerializer(data=data, context={"user": user})

        assert serializer.is_valid()

    def test_note_invalid_category(self, user):
        """Test serializer rejects invalid category_id."""
        data = {"title": "Test", "category_id": 99999}
        serializer = NoteCreateSerializer(data=data, context={"user": user})

        assert not serializer.is_valid()
        assert "category_id" in serializer.errors

    def test_note_category_from_other_user(self, user):
        """Test serializer rejects category from another user."""
        other_user = User.objects.create_user(email="other@example.com", password="pass123")
        other_category = Category.objects.create(user=other_user, name="Other")

        data = {"title": "Test", "category_id": other_category.id}
        serializer = NoteCreateSerializer(data=data, context={"user": user})

        assert not serializer.is_valid()
        assert "category_id" in serializer.errors

    def test_note_title_stripped(self, user):
        """Test serializer strips whitespace from title."""
        data = {"title": "  My Note  ", "content": "Content"}
        serializer = NoteCreateSerializer(data=data, context={"user": user})

        assert serializer.is_valid()
        assert serializer.validated_data["title"] == "My Note"


@pytest.mark.django_db
class TestNoteUpdateSerializer:
    """Tests for NoteUpdateSerializer."""

    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(email="test@example.com", password="testpass123")

    def test_note_partial_update(self, user):
        """Test serializer supports partial updates."""
        data = {"title": "Updated Title"}
        serializer = NoteUpdateSerializer(data=data, partial=True, context={"user": user})

        assert serializer.is_valid()
        assert "title" in serializer.validated_data
        assert "content" not in serializer.validated_data


@pytest.mark.django_db
class TestNoteListSerializer:
    """Tests for NoteListSerializer."""

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
            content="A" * 500,  # Long content
        )

    def test_note_list_serializer_content_preview(self, note):
        """Test serializer includes content preview (first 200 chars)."""
        serializer = NoteListSerializer(note)

        assert "content_preview" in serializer.data
        assert len(serializer.data["content_preview"]) == 200
        assert serializer.data["content_preview"] == "A" * 200

    def test_note_list_serializer_short_content(self, user):
        """Test serializer handles content shorter than 200 chars."""
        note = Note.objects.create(user=user, title="Test", content="Short")
        serializer = NoteListSerializer(note)

        assert serializer.data["content_preview"] == "Short"

    def test_note_list_serializer_includes_category(self, note):
        """Test serializer includes nested category."""
        serializer = NoteListSerializer(note)

        assert "category" in serializer.data
        assert serializer.data["category"]["id"] == note.category.id
        assert serializer.data["category"]["name"] == "Test Category"

    def test_note_list_serializer_null_category(self, user):
        """Test serializer handles null category."""
        note = Note.objects.create(user=user, title="Test", content="Content")
        serializer = NoteListSerializer(note)

        assert serializer.data["category"] is None


@pytest.mark.django_db
class TestNoteDetailSerializer:
    """Tests for NoteDetailSerializer."""

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
            content="Full content here",
        )

    def test_note_detail_serializer_includes_full_content(self, note):
        """Test serializer includes full content (not preview)."""
        serializer = NoteDetailSerializer(note)

        assert "content" in serializer.data
        assert "content_preview" not in serializer.data
        assert serializer.data["content"] == "Full content here"

    def test_note_detail_serializer_includes_timestamps(self, note):
        """Test serializer includes created_at and updated_at."""
        serializer = NoteDetailSerializer(note)

        assert "created_at" in serializer.data
        assert "updated_at" in serializer.data

    def test_note_detail_serializer_includes_category(self, note):
        """Test serializer includes nested category."""
        serializer = NoteDetailSerializer(note)

        assert "category" in serializer.data
        assert serializer.data["category"]["id"] == note.category.id
