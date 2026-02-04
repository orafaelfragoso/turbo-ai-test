"""
Tests for notes and categories API views.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.notes.models import Category, Note

User = get_user_model()


@pytest.fixture
def api_client():
    """Create an API client."""
    return APIClient()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(email="test@example.com", password="testpass123")


@pytest.fixture
def authenticated_client(api_client, user):
    """Create an authenticated API client."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def category(user):
    """Create a test category."""
    return Category.objects.create(user=user, name="Test Category")


@pytest.fixture
def note(user, category):
    """Create a test note."""
    return Note.objects.create(user=user, category=category, title="Test Note", content="Test content")


@pytest.mark.django_db
class TestCategoryListView:
    """Tests for listing and creating categories."""

    def test_list_categories_authenticated(self, authenticated_client, user):
        """Test listing categories as authenticated user."""
        Category.objects.create(user=user, name="Work")
        Category.objects.create(user=user, name="Personal")

        response = authenticated_client.get("/api/categories/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert response.data[0]["name"] == "Work"

    def test_list_categories_unauthenticated(self, api_client):
        """Test listing categories without authentication fails."""
        response = api_client.get("/api/categories/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_categories_multi_tenant_isolation(self, authenticated_client, user):
        """Test users only see their own categories."""
        other_user = User.objects.create_user(email="other@example.com", password="pass123")

        Category.objects.create(user=user, name="My Category")
        Category.objects.create(user=other_user, name="Other Category")

        response = authenticated_client.get("/api/categories/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "My Category"

    def test_create_category_authenticated(self, authenticated_client):
        """Test creating a category as authenticated user."""
        data = {"name": "Work", "color": "#10b981"}

        response = authenticated_client.post("/api/categories/", data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Work"
        assert response.data["color"] == "#10B981"  # Color is normalized to uppercase
        assert "id" in response.data
        assert "note_count" in response.data
        assert response.data["note_count"] == 0

    def test_create_category_unauthenticated(self, api_client):
        """Test creating a category without authentication fails."""
        data = {"name": "Work", "color": "#10b981"}

        response = api_client.post("/api/categories/", data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_category_duplicate_name(self, authenticated_client, user):
        """Test creating category with duplicate name fails."""
        Category.objects.create(user=user, name="Work")

        data = {"name": "Work", "color": "#10b981"}
        response = authenticated_client.post("/api/categories/", data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_create_category_invalid_color(self, authenticated_client):
        """Test creating category with invalid color fails."""
        data = {"name": "Work", "color": "invalid"}

        response = authenticated_client.post("/api/categories/", data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "color" in response.data


@pytest.mark.django_db
class TestCategoryDetailView:
    """Tests for retrieving, updating, and deleting categories."""

    def test_retrieve_category_authenticated(self, authenticated_client, category):
        """Test retrieving a category as authenticated user."""
        response = authenticated_client.get(f"/api/categories/{category.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == category.id
        assert response.data["name"] == "Test Category"

    def test_retrieve_category_other_user(self, authenticated_client, user):
        """Test retrieving another user's category returns 404."""
        other_user = User.objects.create_user(email="other@example.com", password="pass123")
        other_category = Category.objects.create(user=other_user, name="Other")

        response = authenticated_client.get(f"/api/categories/{other_category.id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_category_not_found(self, authenticated_client):
        """Test retrieving non-existent category returns 404."""
        response = authenticated_client.get("/api/categories/99999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_category_authenticated(self, authenticated_client, category):
        """Test updating a category as authenticated user."""
        data = {"name": "Updated Name", "color": "#f59e0b"}

        response = authenticated_client.patch(f"/api/categories/{category.id}/", data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Name"
        assert response.data["color"] == "#F59E0B"  # Color is normalized to uppercase

    def test_update_category_partial(self, authenticated_client, category):
        """Test partial update of category."""
        data = {"name": "Updated Name"}

        response = authenticated_client.patch(f"/api/categories/{category.id}/", data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Name"
        # Color should remain unchanged
        assert response.data["color"] == category.color

    def test_update_category_other_user(self, authenticated_client, user):
        """Test updating another user's category returns 404."""
        other_user = User.objects.create_user(email="other@example.com", password="pass123")
        other_category = Category.objects.create(user=other_user, name="Other")

        data = {"name": "Hacked"}
        response = authenticated_client.patch(f"/api/categories/{other_category.id}/", data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_category_authenticated(self, authenticated_client, category):
        """Test deleting a category as authenticated user."""
        response = authenticated_client.delete(f"/api/categories/{category.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(id=category.id).exists()

    def test_delete_random_thoughts_category(self, authenticated_client, user):
        """Test deleting 'Random Thoughts' category is prevented."""
        random_thoughts = Category.objects.create(user=user, name="Random Thoughts")

        response = authenticated_client.delete(f"/api/categories/{random_thoughts.id}/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Category.objects.filter(id=random_thoughts.id).exists()

    def test_delete_category_other_user(self, authenticated_client, user):
        """Test deleting another user's category returns 404."""
        other_user = User.objects.create_user(email="other@example.com", password="pass123")
        other_category = Category.objects.create(user=other_user, name="Other")

        response = authenticated_client.delete(f"/api/categories/{other_category.id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestNoteListView:
    """Tests for listing and creating notes."""

    def test_list_notes_authenticated(self, authenticated_client, user, category):
        """Test listing notes as authenticated user."""
        Note.objects.create(user=user, category=category, title="Note 1")
        Note.objects.create(user=user, category=category, title="Note 2")

        response = authenticated_client.get("/api/notes/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        assert len(response.data["results"]) == 2

    def test_list_notes_unauthenticated(self, api_client):
        """Test listing notes without authentication fails."""
        response = api_client.get("/api/notes/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_notes_multi_tenant_isolation(self, authenticated_client, user):
        """Test users only see their own notes."""
        other_user = User.objects.create_user(email="other@example.com", password="pass123")

        Note.objects.create(user=user, title="My Note")
        Note.objects.create(user=other_user, title="Other Note")

        response = authenticated_client.get("/api/notes/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["title"] == "My Note"

    def test_list_notes_filter_by_category(self, authenticated_client, user, category):
        """Test filtering notes by category."""
        other_category = Category.objects.create(user=user, name="Other")

        Note.objects.create(user=user, category=category, title="Cat1 Note")
        Note.objects.create(user=user, category=other_category, title="Cat2 Note")

        response = authenticated_client.get(f"/api/notes/?category_id={category.id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["title"] == "Cat1 Note"

    def test_list_notes_search(self, authenticated_client, user):
        """Test searching notes."""
        Note.objects.create(user=user, title="Python Tutorial")
        Note.objects.create(user=user, title="JavaScript Guide")

        response = authenticated_client.get("/api/notes/?search=Python")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert "Python" in response.data["results"][0]["title"]

    def test_list_notes_pagination(self, authenticated_client, user):
        """Test notes list pagination."""
        for i in range(25):
            Note.objects.create(user=user, title=f"Note {i}")

        response = authenticated_client.get("/api/notes/?page_size=10")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 10
        assert response.data["count"] == 25

    def test_create_note_authenticated(self, authenticated_client, category):
        """Test creating a note as authenticated user."""
        data = {"title": "My Note", "content": "My content", "category_id": category.id}

        response = authenticated_client.post("/api/notes/", data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "My Note"
        assert response.data["content"] == "My content"
        assert response.data["category"]["id"] == category.id

    def test_create_note_unauthenticated(self, api_client):
        """Test creating a note without authentication fails."""
        data = {"title": "My Note"}

        response = api_client.post("/api/notes/", data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_note_without_category(self, authenticated_client, user):
        """Test creating note without category uses default."""
        Category.objects.create(user=user, name="Random Thoughts")

        data = {"title": "My Note"}
        response = authenticated_client.post("/api/notes/", data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["category"]["name"] == "Random Thoughts"

    def test_create_note_invalid_category(self, authenticated_client):
        """Test creating note with invalid category fails."""
        data = {"title": "My Note", "category_id": 99999}

        response = authenticated_client.post("/api/notes/", data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "category_id" in response.data


@pytest.mark.django_db
class TestNoteDetailView:
    """Tests for retrieving, updating, and deleting notes."""

    def test_retrieve_note_authenticated(self, authenticated_client, note):
        """Test retrieving a note as authenticated user."""
        response = authenticated_client.get(f"/api/notes/{note.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert str(response.data["id"]) == str(note.id)
        assert response.data["title"] == "Test Note"
        assert response.data["content"] == "Test content"

    def test_retrieve_note_other_user(self, authenticated_client, user):
        """Test retrieving another user's note returns 404."""
        other_user = User.objects.create_user(email="other@example.com", password="pass123")
        other_note = Note.objects.create(user=other_user, title="Other")

        response = authenticated_client.get(f"/api/notes/{other_note.id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_note_not_found(self, authenticated_client):
        """Test retrieving non-existent note returns 404."""
        import uuid

        fake_uuid = uuid.uuid4()
        response = authenticated_client.get(f"/api/notes/{fake_uuid}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_note_authenticated(self, authenticated_client, note):
        """Test updating a note as authenticated user."""
        data = {"title": "Updated Title", "content": "Updated content"}

        response = authenticated_client.patch(f"/api/notes/{note.id}/", data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Title"
        assert response.data["content"] == "Updated content"

    def test_update_note_partial(self, authenticated_client, note):
        """Test partial update of note."""
        data = {"title": "Updated Title"}

        response = authenticated_client.patch(f"/api/notes/{note.id}/", data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Title"
        # Content should remain unchanged
        assert response.data["content"] == "Test content"

    def test_update_note_change_category(self, authenticated_client, user, note):
        """Test changing note category."""
        new_category = Category.objects.create(user=user, name="New Category")

        data = {"category_id": new_category.id}
        response = authenticated_client.patch(f"/api/notes/{note.id}/", data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["category"]["id"] == new_category.id

    def test_update_note_other_user(self, authenticated_client, user):
        """Test updating another user's note returns 404."""
        other_user = User.objects.create_user(email="other@example.com", password="pass123")
        other_note = Note.objects.create(user=other_user, title="Other")

        data = {"title": "Hacked"}
        response = authenticated_client.patch(f"/api/notes/{other_note.id}/", data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_note_authenticated(self, authenticated_client, note):
        """Test deleting a note as authenticated user."""
        note_id = note.id

        response = authenticated_client.delete(f"/api/notes/{note_id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Note.objects.filter(id=note_id).exists()

    def test_delete_note_other_user(self, authenticated_client, user):
        """Test deleting another user's note returns 404."""
        other_user = User.objects.create_user(email="other@example.com", password="pass123")
        other_note = Note.objects.create(user=other_user, title="Other")

        response = authenticated_client.delete(f"/api/notes/{other_note.id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestNotesIntegration:
    """Integration tests for the notes feature."""

    def test_end_to_end_workflow(self, authenticated_client, user):
        """Test complete workflow: create category, create note, update, delete."""
        # Create category
        category_data = {"name": "Work", "color": "#10b981"}
        cat_response = authenticated_client.post("/api/categories/", category_data, format="json")
        assert cat_response.status_code == status.HTTP_201_CREATED
        category_id = cat_response.data["id"]

        # Create note
        note_data = {"title": "Meeting Notes", "content": "Discuss project", "category_id": category_id}
        note_response = authenticated_client.post("/api/notes/", note_data, format="json")
        assert note_response.status_code == status.HTTP_201_CREATED
        note_id = note_response.data["id"]

        # Update note
        update_data = {"title": "Updated Meeting Notes"}
        update_response = authenticated_client.patch(f"/api/notes/{note_id}/", update_data, format="json")
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.data["title"] == "Updated Meeting Notes"

        # Delete note
        delete_response = authenticated_client.delete(f"/api/notes/{note_id}/")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Delete category
        delete_cat_response = authenticated_client.delete(f"/api/categories/{category_id}/")
        assert delete_cat_response.status_code == status.HTTP_204_NO_CONTENT

    def test_category_deletion_orphans_notes(self, authenticated_client, user, category):
        """Test deleting category sets notes to NULL."""
        note = Note.objects.create(user=user, category=category, title="Test")

        response = authenticated_client.delete(f"/api/categories/{category.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Note should still exist with NULL category
        note.refresh_from_db()
        assert note.category is None
