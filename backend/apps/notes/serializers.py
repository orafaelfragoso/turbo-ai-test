"""
Serializers for notes and categories.
Handles validation and data transformation only.
Business logic is in services.py.
"""

from django.core.cache import cache
from rest_framework import serializers

from .models import Category, Note


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating categories.
    """

    class Meta:
        model = Category
        fields = ["id", "name", "color", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        """Validate category name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Category name cannot be empty.")
        return value.strip()

    def validate_color(self, value):
        """Validate hex color format."""
        if not value.startswith("#") or len(value) != 7:
            raise serializers.ValidationError(
                "Color must be a valid hex color code (e.g., #6366f1)."
            )
        # Check if remaining characters are valid hex
        try:
            int(value[1:], 16)
        except ValueError:
            raise serializers.ValidationError(
                "Color must be a valid hex color code (e.g., #6366f1)."
            ) from None
        return value.upper()


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing categories with note counts.
    """

    note_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "color", "note_count", "created_at", "updated_at"]
        read_only_fields = ["id", "name", "color", "note_count", "created_at", "updated_at"]

    def get_note_count(self, obj):
        """Get note count from Redis cache or database."""
        cache_key = f"category:{obj.id}:note_count"
        note_count = cache.get(cache_key)

        if note_count is None:
            # Cache miss - query database and populate cache
            note_count = obj.notes.count()
            cache.set(cache_key, note_count, timeout=3600)  # 1 hour TTL

        return note_count


class CategoryDetailSerializer(CategoryListSerializer):
    """
    Serializer for category detail responses.
    Identical to list serializer.
    """

    pass


class CategoryNestedSerializer(serializers.ModelSerializer):
    """
    Nested serializer for category in note responses.
    """

    class Meta:
        model = Category
        fields = ["id", "name", "color"]
        read_only_fields = ["id", "name", "color"]


class NoteCreateSerializer(serializers.Serializer):
    """
    Serializer for creating notes.
    """

    title = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Note title (max 255 characters)",
    )
    content = serializers.CharField(
        max_length=100000,
        required=False,
        allow_blank=True,
        help_text="Note content (max 100,000 characters)",
    )
    category_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Category ID (must belong to user)",
    )

    def validate_title(self, value):
        """Strip and validate title."""
        if value:
            return value.strip()
        return ""

    def validate_category_id(self, value):
        """Validate category exists and belongs to user."""
        if value is None:
            return value

        user = self.context.get("user")
        if not user:
            raise serializers.ValidationError("User context is required.")

        # Check if category exists and belongs to user
        if not Category.objects.filter(id=value, user=user).exists():
            raise serializers.ValidationError(
                "Category does not exist or does not belong to you."
            )

        return value


class NoteUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating notes (partial update).
    """

    title = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Note title (max 255 characters)",
    )
    content = serializers.CharField(
        max_length=100000,
        required=False,
        allow_blank=True,
        help_text="Note content (max 100,000 characters)",
    )
    category_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Category ID (must belong to user)",
    )

    def validate_title(self, value):
        """Strip and validate title."""
        if value:
            return value.strip()
        return ""

    def validate_category_id(self, value):
        """Validate category exists and belongs to user."""
        if value is None:
            return value

        user = self.context.get("user")
        if not user:
            raise serializers.ValidationError("User context is required.")

        # Check if category exists and belongs to user
        if not Category.objects.filter(id=value, user=user).exists():
            raise serializers.ValidationError(
                "Category does not exist or does not belong to you."
            )

        return value


class NoteListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing notes with content preview.
    """

    content_preview = serializers.SerializerMethodField()
    category = CategoryNestedSerializer(read_only=True)

    class Meta:
        model = Note
        fields = ["id", "title", "content_preview", "category", "updated_at"]
        read_only_fields = ["id", "title", "content_preview", "category", "updated_at"]

    def get_content_preview(self, obj):
        """Return first 200 characters of content."""
        if obj.content:
            return obj.content[:200]
        return ""


class NoteDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for note detail responses with full content.
    """

    category = CategoryNestedSerializer(read_only=True)

    class Meta:
        model = Note
        fields = ["id", "title", "content", "category", "created_at", "updated_at"]
        read_only_fields = ["id", "title", "content", "category", "created_at", "updated_at"]
