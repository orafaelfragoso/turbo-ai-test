"""
Tests for notes and categories services.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.exceptions import NotFound, ValidationError

from apps.notes.models import Category, Note
from apps.notes.services import CategoryService, NoteService

User = get_user_model()


@pytest.mark.django_db
class TestCategoryService:
    """Tests for CategoryService."""

    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(email="test@example.com", password="testpass123")

    @pytest.fixture
    def category(self, user):
        """Create a test category."""
        return Category.objects.create(user=user, name="Test Category")

    def test_list_categories(self, user):
        """Test listing categories for a user."""
        cat1 = Category.objects.create(user=user, name="First")
        cat2 = Category.objects.create(user=user, name="Second")

        categories = list(CategoryService.list_categories(user))

        assert len(categories) == 2
        assert categories[0] == cat1
        assert categories[1] == cat2

    def test_list_categories_multi_tenant_isolation(self, user):
        """Test categories are isolated per user."""
        other_user = User.objects.create_user(email="other@example.com", password="pass123")

        Category.objects.create(user=user, name="User1 Category")
        Category.objects.create(user=other_user, name="User2 Category")

        user_categories = list(CategoryService.list_categories(user))

        assert len(user_categories) == 1
        assert user_categories[0].name == "User1 Category"

    def test_create_category(self, user):
        """Test creating a category."""
        data = {"name": "Work", "color": "#10b981"}

        category = CategoryService.create_category(user, data)

        assert category.id is not None
        assert category.user == user
        assert category.name == "Work"
        assert category.color == "#10b981"

    def test_create_category_initializes_cache(self, user):
        """Test creating a category initializes note count cache."""
        data = {"name": "Work", "color": "#10b981"}

        category = CategoryService.create_category(user, data)

        cache_key = f"category:{category.id}:note_count"
        cached_count = cache.get(cache_key)

        assert cached_count == 0

    def test_create_category_duplicate_name(self, user):
        """Test creating a category with duplicate name fails."""
        Category.objects.create(user=user, name="Work")

        data = {"name": "Work", "color": "#10b981"}

        with pytest.raises(ValidationError) as exc:
            CategoryService.create_category(user, data)

        assert "name" in exc.value.detail

    def test_create_category_duplicate_name_different_user(self, user):
        """Test different users can have categories with same name."""
        other_user = User.objects.create_user(email="other@example.com", password="pass123")

        Category.objects.create(user=user, name="Work")

        data = {"name": "Work", "color": "#10b981"}
        category = CategoryService.create_category(other_user, data)

        assert category.name == "Work"
        assert category.user == other_user

    def test_get_category(self, user, category):
        """Test getting a category by ID."""
        result = CategoryService.get_category(user, category.id)

        assert result == category

    def test_get_category_not_found(self, user):
        """Test getting non-existent category raises NotFound."""
        with pytest.raises(NotFound):
            CategoryService.get_category(user, 99999)

    def test_get_category_other_user(self, user, category):
        """Test getting category from another user raises NotFound."""
        other_user = User.objects.create_user(email="other@example.com", password="pass123")

        with pytest.raises(NotFound):
            CategoryService.get_category(other_user, category.id)

    def test_update_category_name(self, user, category):
        """Test updating category name."""
        data = {"name": "Updated Name"}

        updated_category = CategoryService.update_category(user, category.id, data)

        assert updated_category.name == "Updated Name"
        assert updated_category.id == category.id

    def test_update_category_color(self, user, category):
        """Test updating category color."""
        data = {"color": "#f59e0b"}

        updated_category = CategoryService.update_category(user, category.id, data)

        assert updated_category.color == "#f59e0b"

    def test_update_category_duplicate_name(self, user):
        """Test updating to duplicate name fails."""
        Category.objects.create(user=user, name="Work")
        category2 = Category.objects.create(user=user, name="Personal")

        data = {"name": "Work"}

        with pytest.raises(ValidationError) as exc:
            CategoryService.update_category(user, category2.id, data)

        assert "name" in exc.value.detail

    def test_update_category_same_name(self, user, category):
        """Test updating to same name is allowed."""
        data = {"name": category.name}

        updated_category = CategoryService.update_category(user, category.id, data)

        assert updated_category.name == category.name

    def test_delete_category(self, user, category):
        """Test deleting a category."""
        category_id = category.id

        CategoryService.delete_category(user, category_id)

        assert not Category.objects.filter(id=category_id).exists()

    def test_delete_category_updates_notes(self, user, category):
        """Test deleting category sets notes' category to NULL."""
        note = Note.objects.create(user=user, category=category, title="Test")

        CategoryService.delete_category(user, category.id)

        note.refresh_from_db()
        assert note.category is None

    def test_delete_category_removes_cache(self, user, category):
        """Test deleting category removes cache entry."""
        cache_key = f"category:{category.id}:note_count"
        cache.set(cache_key, 5, timeout=3600)

        CategoryService.delete_category(user, category.id)

        assert cache.get(cache_key) is None

    def test_delete_random_thoughts_category(self, user):
        """Test deleting 'Random Thoughts' category is prevented."""
        category = Category.objects.create(user=user, name="Random Thoughts")

        with pytest.raises(ValidationError) as exc:
            CategoryService.delete_category(user, category.id)

        assert "Random Thoughts" in str(exc.value.detail)

    def test_delete_category_not_found(self, user):
        """Test deleting non-existent category raises NotFound."""
        with pytest.raises(NotFound):
            CategoryService.delete_category(user, 99999)


@pytest.mark.django_db
class TestNoteService:
    """Tests for NoteService."""

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
        return Note.objects.create(user=user, category=category, title="Test Note")

    def test_create_note_with_category(self, user, category):
        """Test creating a note with specified category."""
        data = {"title": "My Note", "content": "Content", "category_id": category.id}

        note = NoteService.create_note(user, data)

        assert note.user == user
        assert note.category == category
        assert note.title == "My Note"
        assert note.content == "Content"

    def test_create_note_increments_cache(self, user, category):
        """Test creating a note increments category cache."""
        cache_key = f"category:{category.id}:note_count"
        cache.set(cache_key, 5, timeout=3600)

        data = {"title": "Test", "category_id": category.id}
        NoteService.create_note(user, data)

        assert cache.get(cache_key) == 6

    def test_create_note_default_category_random_thoughts(self, user):
        """Test creating note without category uses Random Thoughts."""
        random_thoughts = Category.objects.create(user=user, name="Random Thoughts")

        data = {"title": "Test"}
        note = NoteService.create_note(user, data)

        assert note.category == random_thoughts

    def test_create_note_default_category_most_recent(self, user):
        """Test creating note uses most recent category if no Random Thoughts."""
        cat1 = Category.objects.create(user=user, name="First")
        cat2 = Category.objects.create(user=user, name="Second")

        data = {"title": "Test"}
        note = NoteService.create_note(user, data)

        assert note.category == cat2  # Most recent

    def test_create_note_no_categories(self, user):
        """Test creating note without categories sets category to NULL."""
        data = {"title": "Test"}
        note = NoteService.create_note(user, data)

        assert note.category is None

    def test_create_note_invalid_category(self, user):
        """Test creating note with invalid category_id fails."""
        data = {"title": "Test", "category_id": 99999}

        with pytest.raises(ValidationError) as exc:
            NoteService.create_note(user, data)

        assert "category_id" in exc.value.detail

    def test_list_notes(self, user):
        """Test listing notes for a user."""
        note1 = Note.objects.create(user=user, title="First")
        note2 = Note.objects.create(user=user, title="Second")

        notes = list(NoteService.list_notes(user))

        assert len(notes) == 2
        # Should be ordered by updated_at descending
        assert notes[0] == note2
        assert notes[1] == note1

    def test_list_notes_filter_by_category(self, user, category):
        """Test listing notes filtered by category."""
        other_category = Category.objects.create(user=user, name="Other")

        note1 = Note.objects.create(user=user, category=category, title="Cat1 Note")
        Note.objects.create(user=user, category=other_category, title="Cat2 Note")

        filters = {"category_id": category.id}
        notes = list(NoteService.list_notes(user, filters))

        assert len(notes) == 1
        assert notes[0] == note1

    def test_list_notes_search(self, user):
        """Test listing notes with search filter."""
        Note.objects.create(user=user, title="Python Tutorial", content="Learn Python")
        Note.objects.create(user=user, title="JavaScript Guide", content="Learn JS")

        filters = {"search": "Python"}
        notes = list(NoteService.list_notes(user, filters))

        assert len(notes) == 1
        assert "Python" in notes[0].title

    def test_list_notes_search_in_content(self, user):
        """Test search works on content as well as title."""
        Note.objects.create(user=user, title="Guide", content="Learn Python here")
        Note.objects.create(user=user, title="Tutorial", content="Learn JS here")

        filters = {"search": "Python"}
        notes = list(NoteService.list_notes(user, filters))

        assert len(notes) == 1
        assert "Python" in notes[0].content

    def test_list_notes_invalid_category(self, user):
        """Test listing with invalid category_id fails."""
        filters = {"category_id": 99999}

        with pytest.raises(ValidationError) as exc:
            NoteService.list_notes(user, filters)

        assert "category_id" in exc.value.detail

    def test_list_notes_multi_tenant_isolation(self, user):
        """Test notes are isolated per user."""
        other_user = User.objects.create_user(email="other@example.com", password="pass123")

        Note.objects.create(user=user, title="User1 Note")
        Note.objects.create(user=other_user, title="User2 Note")

        notes = list(NoteService.list_notes(user))

        assert len(notes) == 1
        assert notes[0].title == "User1 Note"

    def test_get_note(self, user, note):
        """Test getting a note by UUID."""
        result = NoteService.get_note(user, note.id)

        assert result == note

    def test_get_note_not_found(self, user):
        """Test getting non-existent note raises NotFound."""
        import uuid

        with pytest.raises(NotFound):
            NoteService.get_note(user, uuid.uuid4())

    def test_get_note_other_user(self, user, note):
        """Test getting note from another user raises NotFound."""
        other_user = User.objects.create_user(email="other@example.com", password="pass123")

        with pytest.raises(NotFound):
            NoteService.get_note(other_user, note.id)

    def test_update_note_title(self, user, note):
        """Test updating note title."""
        data = {"title": "Updated Title"}

        updated_note = NoteService.update_note(user, note.id, data)

        assert updated_note.title == "Updated Title"

    def test_update_note_content(self, user, note):
        """Test updating note content."""
        data = {"content": "Updated content"}

        updated_note = NoteService.update_note(user, note.id, data)

        assert updated_note.content == "Updated content"

    def test_update_note_category(self, user, note):
        """Test updating note category."""
        new_category = Category.objects.create(user=user, name="New Category")

        data = {"category_id": new_category.id}
        updated_note = NoteService.update_note(user, note.id, data)

        assert updated_note.category == new_category

    def test_update_note_category_updates_cache(self, user, category):
        """Test updating note category updates both old and new cache."""
        new_category = Category.objects.create(user=user, name="New Category")
        note = Note.objects.create(user=user, category=category, title="Test")

        # Set cache values
        old_cache_key = f"category:{category.id}:note_count"
        new_cache_key = f"category:{new_category.id}:note_count"
        cache.set(old_cache_key, 5, timeout=3600)
        cache.set(new_cache_key, 3, timeout=3600)

        data = {"category_id": new_category.id}
        NoteService.update_note(user, note.id, data)

        # Old category count should be decremented
        assert cache.get(old_cache_key) == 4
        # New category count should be incremented
        assert cache.get(new_cache_key) == 4

    def test_update_note_remove_category(self, user, note):
        """Test removing category from note."""
        data = {"category_id": None}

        updated_note = NoteService.update_note(user, note.id, data)

        assert updated_note.category is None

    def test_update_note_invalid_category(self, user, note):
        """Test updating with invalid category_id fails."""
        data = {"category_id": 99999}

        with pytest.raises(ValidationError) as exc:
            NoteService.update_note(user, note.id, data)

        assert "category_id" in exc.value.detail

    def test_delete_note(self, user, note):
        """Test deleting a note."""
        note_id = note.id

        NoteService.delete_note(user, note_id)

        assert not Note.objects.filter(id=note_id).exists()

    def test_delete_note_decrements_cache(self, user, category):
        """Test deleting note decrements category cache."""
        note = Note.objects.create(user=user, category=category, title="Test")

        cache_key = f"category:{category.id}:note_count"
        cache.set(cache_key, 5, timeout=3600)

        NoteService.delete_note(user, note.id)

        assert cache.get(cache_key) == 4

    def test_delete_note_not_found(self, user):
        """Test deleting non-existent note raises NotFound."""
        import uuid

        with pytest.raises(NotFound):
            NoteService.delete_note(user, uuid.uuid4())
