"""
Service Layer for notes and categories business logic.
All business logic resides here, keeping views and serializers thin.
"""

from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import NotFound, ValidationError

from .models import Category, Note


class CategoryService:
    """
    Service class for category operations.
    Implements Service Layer Pattern.
    """

    @staticmethod
    def list_categories(user):
        """
        List all categories for a user with note counts.

        Args:
            user: User instance

        Returns:
            QuerySet of Category objects ordered by created_at
        """
        return Category.objects.filter(user=user).order_by("created_at")

    @staticmethod
    @transaction.atomic
    def create_category(user, data):
        """
        Create a new category for a user.

        Args:
            user: User instance
            data: Dict containing name and optional color

        Returns:
            Created Category instance

        Raises:
            ValidationError: If category name already exists for user
        """
        name = data.get("name", "").strip()
        color = data.get("color", "#6366f1")

        # Check for duplicate category name
        if Category.objects.filter(user=user, name=name).exists():
            raise ValidationError(
                {"name": ["A category with this name already exists."]}
            )

        # Create category
        category = Category.objects.create(user=user, name=name, color=color)

        # Initialize note count in cache
        cache_key = f"category:{category.id}:note_count"
        cache.set(cache_key, 0, timeout=3600)

        return category

    @staticmethod
    def get_category(user, category_id):
        """
        Get a single category for a user.

        Args:
            user: User instance
            category_id: Category ID

        Returns:
            Category instance

        Raises:
            NotFound: If category doesn't exist or belongs to another user
        """
        try:
            return Category.objects.get(id=category_id, user=user)
        except Category.DoesNotExist:
            raise NotFound("Category not found.") from None

    @staticmethod
    @transaction.atomic
    def update_category(user, category_id, data):
        """
        Update a category for a user.

        Args:
            user: User instance
            category_id: Category ID
            data: Dict containing optional name and/or color

        Returns:
            Updated Category instance

        Raises:
            NotFound: If category doesn't exist or belongs to another user
            ValidationError: If new name conflicts with existing category
        """
        category = CategoryService.get_category(user, category_id)

        # Check if name is being updated and if it conflicts
        new_name = data.get("name")
        if new_name is not None:
            new_name = new_name.strip()
            # Check for duplicate name (excluding current category)
            if (
                new_name != category.name
                and Category.objects.filter(user=user, name=new_name).exists()
            ):
                raise ValidationError(
                    {"name": ["A category with this name already exists."]}
                )
            category.name = new_name

        # Update color if provided
        new_color = data.get("color")
        if new_color is not None:
            category.color = new_color

        category.save()
        return category

    @staticmethod
    @transaction.atomic
    def delete_category(user, category_id):
        """
        Delete a category for a user.

        Args:
            user: User instance
            category_id: Category ID

        Raises:
            NotFound: If category doesn't exist or belongs to another user
            ValidationError: If attempting to delete "Random Thoughts" category
        """
        category = CategoryService.get_category(user, category_id)

        # Prevent deletion of "Random Thoughts" category
        if category.name == "Random Thoughts":
            raise ValidationError(
                {"detail": "Cannot delete the 'Random Thoughts' category."}
            )

        # Update all notes in this category to have no category
        Note.objects.filter(category=category).update(category=None)

        # Remove category note count from cache
        cache_key = f"category:{category.id}:note_count"
        cache.delete(cache_key)

        # Delete category
        category.delete()


class NoteService:
    """
    Service class for note operations.
    Implements Service Layer Pattern.
    """

    @staticmethod
    def _get_default_category(user):
        """
        Get the default category for a user.
        Priority: Random Thoughts → Most recent category → None

        Args:
            user: User instance

        Returns:
            Category instance or None
        """
        # Try to get "Random Thoughts" category
        try:
            return Category.objects.get(user=user, name="Random Thoughts")
        except Category.DoesNotExist:
            pass

        # Fall back to most recently created category
        category = Category.objects.filter(user=user).order_by("-created_at").first()
        return category

    @staticmethod
    @transaction.atomic
    def create_note(user, data):
        """
        Create a new note for a user.

        Args:
            user: User instance
            data: Dict containing optional title, content, and category_id

        Returns:
            Created Note instance

        Raises:
            ValidationError: If category_id doesn't belong to user
        """
        title = data.get("title", "")
        content = data.get("content", "")
        category_id = data.get("category_id")

        # Determine category
        category = None
        if category_id is not None:
            # Validate category belongs to user
            try:
                category = Category.objects.get(id=category_id, user=user)
            except Category.DoesNotExist:
                raise ValidationError(
                    {"category_id": ["Category does not exist or does not belong to you."]}
                ) from None
        else:
            # Use default category
            category = NoteService._get_default_category(user)

        # Create note
        note = Note.objects.create(
            user=user, category=category, title=title, content=content
        )

        # Increment category note count in cache
        if category:
            cache_key = f"category:{category.id}:note_count"
            try:
                cache.incr(cache_key)
            except ValueError:
                # Cache key doesn't exist, initialize it
                note_count = Note.objects.filter(category=category).count()
                cache.set(cache_key, note_count, timeout=3600)

        return note

    @staticmethod
    def list_notes(user, filters=None):
        """
        List notes for a user with optional filtering.

        Args:
            user: User instance
            filters: Dict containing optional category_id and search

        Returns:
            QuerySet of Note objects
        """
        filters = filters or {}
        queryset = Note.objects.filter(user=user).select_related("category")

        # Filter by category if provided
        category_id = filters.get("category_id")
        if category_id is not None:
            # Validate category belongs to user
            if not Category.objects.filter(id=category_id, user=user).exists():
                raise ValidationError(
                    {"category_id": ["Category does not exist or does not belong to you."]}
                )
            queryset = queryset.filter(category_id=category_id)

        # Search in title and content if provided
        search = filters.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )

        return queryset.order_by("-updated_at")

    @staticmethod
    def get_note(user, note_uuid):
        """
        Get a single note for a user.

        Args:
            user: User instance
            note_uuid: Note UUID

        Returns:
            Note instance with related category

        Raises:
            NotFound: If note doesn't exist or belongs to another user
        """
        try:
            return Note.objects.select_related("category").get(id=note_uuid, user=user)
        except Note.DoesNotExist:
            raise NotFound("Note not found.") from None

    @staticmethod
    @transaction.atomic
    def update_note(user, note_uuid, data):
        """
        Update a note for a user.

        Args:
            user: User instance
            note_uuid: Note UUID
            data: Dict containing optional title, content, and/or category_id

        Returns:
            Updated Note instance

        Raises:
            NotFound: If note doesn't exist or belongs to another user
            ValidationError: If category_id doesn't belong to user
        """
        note = NoteService.get_note(user, note_uuid)
        old_category_id = note.category_id

        # Update title if provided
        if "title" in data:
            note.title = data["title"]

        # Update content if provided
        if "content" in data:
            note.content = data["content"]

        # Update category if provided
        if "category_id" in data:
            new_category_id = data["category_id"]

            if new_category_id is None:
                note.category = None
            else:
                # Validate category belongs to user
                try:
                    note.category = Category.objects.get(id=new_category_id, user=user)
                except Category.DoesNotExist:
                    raise ValidationError(
                        {"category_id": ["Category does not exist or does not belong to you."]}
                    ) from None

        note.save()

        # Update cache if category changed
        new_category_id = note.category_id
        if old_category_id != new_category_id:
            # Decrement old category count
            if old_category_id:
                old_cache_key = f"category:{old_category_id}:note_count"
                try:
                    cache.decr(old_cache_key)
                except ValueError:
                    # Cache key doesn't exist, repopulate it
                    old_count = Note.objects.filter(category_id=old_category_id).count()
                    cache.set(old_cache_key, old_count, timeout=3600)

            # Increment new category count
            if new_category_id:
                new_cache_key = f"category:{new_category_id}:note_count"
                try:
                    cache.incr(new_cache_key)
                except ValueError:
                    # Cache key doesn't exist, repopulate it
                    new_count = Note.objects.filter(category_id=new_category_id).count()
                    cache.set(new_cache_key, new_count, timeout=3600)

        return note

    @staticmethod
    @transaction.atomic
    def delete_note(user, note_uuid):
        """
        Delete a note for a user.

        Args:
            user: User instance
            note_uuid: Note UUID

        Raises:
            NotFound: If note doesn't exist or belongs to another user
        """
        note = NoteService.get_note(user, note_uuid)
        category_id = note.category_id

        # Delete note
        note.delete()

        # Decrement category note count in cache
        if category_id:
            cache_key = f"category:{category_id}:note_count"
            try:
                cache.decr(cache_key)
            except ValueError:
                # Cache key doesn't exist, repopulate it
                note_count = Note.objects.filter(category_id=category_id).count()
                cache.set(cache_key, note_count, timeout=3600)


# Singleton instances for easy access
category_service = CategoryService()
note_service = NoteService()
