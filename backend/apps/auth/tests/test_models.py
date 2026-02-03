"""
Tests for authentication models.
Ensures model methods and properties work correctly.
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test cases for User model."""

    def test_user_str_method(self):
        """Test that User.__str__ returns the email address."""
        email = "testuser@example.com"
        user = User.objects.create_user(
            email=email, password="TestPassword123!"
        )

        assert str(user) == email

    def test_user_creation_with_email(self):
        """Test creating a user with email as primary identifier."""
        email = "newuser@example.com"
        password = "SecurePass123!"

        user = User.objects.create_user(
            email=email, password=password
        )

        assert user.email == email
        assert user.check_password(password)
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_user_email_is_unique(self):
        """Test that email field enforces uniqueness."""
        from django.db import IntegrityError

        email = "unique@example.com"

        User.objects.create_user(email=email, password="Password123!")

        # Attempting to create another user with same email should fail
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email=email, password="Password123!"
            )

    def test_user_timestamps(self):
        """Test that created_at and updated_at are set correctly."""
        user = User.objects.create_user(
            email="timestamps@example.com",
            password="Password123!",
        )

        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.created_at <= user.updated_at

    def test_username_field_is_email(self):
        """Test that USERNAME_FIELD is set to email."""
        assert User.USERNAME_FIELD == "email"

    def test_required_fields_configuration(self):
        """Test that REQUIRED_FIELDS is empty (email is USERNAME_FIELD)."""
        assert User.REQUIRED_FIELDS == []
