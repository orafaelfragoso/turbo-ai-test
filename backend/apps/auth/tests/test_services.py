"""
Tests for authentication service layer.
Tests focus on business logic with 80%+ coverage requirement.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from apps.auth.services import auth_service

User = get_user_model()


@pytest.mark.django_db
class TestAuthService:
    """Test cases for AuthService."""

    def test_register_user_success(self):
        """Test successful user registration."""
        email = "test@example.com"
        password = "SecurePassword123!"

        user_data = auth_service.register_user(email, password)

        assert user_data["email"] == email
        assert "id" in user_data
        assert "created_at" in user_data

        # Verify user was created in database
        user = User.objects.get(email=email)
        assert user.email == email
        assert user.check_password(password)

    def test_register_user_duplicate_email(self):
        """Test registration with duplicate email fails."""
        email = "duplicate@example.com"
        password = "SecurePassword123!"

        # Create first user
        auth_service.register_user(email, password)

        # Attempt to create duplicate
        with pytest.raises(ValidationError) as exc_info:
            auth_service.register_user(email, password)

        assert "email" in exc_info.value.detail
        assert "already exists" in str(exc_info.value.detail["email"][0]).lower()

    def test_register_user_normalizes_email(self):
        """Test that email is normalized (lowercase)."""
        email = "Test@Example.COM"
        password = "SecurePassword123!"

        user_data = auth_service.register_user(email, password)

        assert user_data["email"] == email.lower()

    def test_authenticate_user_success(self):
        """Test successful user authentication."""
        email = "auth@example.com"
        password = "SecurePassword123!"

        # Create user first
        auth_service.register_user(email, password)

        # Authenticate
        tokens = auth_service.authenticate_user(email, password)

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "Bearer"
        assert isinstance(tokens["access_token"], str)
        assert isinstance(tokens["refresh_token"], str)

    def test_authenticate_user_invalid_email(self):
        """Test authentication with non-existent email fails."""
        with pytest.raises(AuthenticationFailed) as exc_info:
            auth_service.authenticate_user("nonexistent@example.com", "password")

        assert "invalid credentials" in str(exc_info.value).lower()

    def test_authenticate_user_invalid_password(self):
        """Test authentication with wrong password fails."""
        email = "wrongpass@example.com"
        password = "CorrectPassword123!"

        # Create user
        auth_service.register_user(email, password)

        # Attempt authentication with wrong password
        with pytest.raises(AuthenticationFailed) as exc_info:
            auth_service.authenticate_user(email, "WrongPassword123!")

        assert "invalid credentials" in str(exc_info.value).lower()

    def test_authenticate_user_inactive_user(self):
        """Test authentication with inactive user fails."""
        email = "inactive@example.com"
        password = "SecurePassword123!"

        # Create and deactivate user
        auth_service.register_user(email, password)
        user = User.objects.get(email=email)
        user.is_active = False
        user.save()

        # Attempt authentication
        with pytest.raises(AuthenticationFailed) as exc_info:
            auth_service.authenticate_user(email, password)

        assert "disabled" in str(exc_info.value).lower()

    def test_refresh_access_token_success(self):
        """Test successful token refresh."""
        email = "refresh@example.com"
        password = "SecurePassword123!"

        # Create user and authenticate
        auth_service.register_user(email, password)
        tokens = auth_service.authenticate_user(email, password)
        refresh_token = tokens["refresh_token"]

        # Refresh access token
        new_tokens = auth_service.refresh_access_token(refresh_token)

        assert "access_token" in new_tokens
        assert new_tokens["token_type"] == "Bearer"
        assert isinstance(new_tokens["access_token"], str)
        # New access token should be different from original
        assert new_tokens["access_token"] != tokens["access_token"]

    def test_refresh_access_token_invalid_token(self):
        """Test token refresh with invalid token fails."""
        with pytest.raises(AuthenticationFailed) as exc_info:
            auth_service.refresh_access_token("invalid-token")

        assert (
            "invalid" in str(exc_info.value).lower()
            or "expired" in str(exc_info.value).lower()
        )

    def test_refresh_access_token_malformed_token(self):
        """Test token refresh with malformed token fails."""
        with pytest.raises(AuthenticationFailed):
            auth_service.refresh_access_token("not.a.jwt.token")
