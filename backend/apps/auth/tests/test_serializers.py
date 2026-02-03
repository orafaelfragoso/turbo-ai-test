"""
Tests for authentication serializers.
Tests data validation and transformation.
"""

from apps.auth.serializers import (
    SigninSerializer,
    SignupSerializer,
    TokenRefreshSerializer,
)


class TestSignupSerializer:
    """Test cases for SignupSerializer."""

    def test_valid_data(self):
        """Test serializer with valid data."""
        data = {
            "email": "test@example.com",
            "password": "SecurePassword123!",
        }
        serializer = SignupSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["email"] == data["email"].lower()

    def test_email_normalization(self):
        """Test email is normalized to lowercase."""
        data = {
            "email": "Test@EXAMPLE.COM",
            "password": "SecurePassword123!",
        }
        serializer = SignupSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["email"] == "test@example.com"

    def test_invalid_email_format(self):
        """Test validation fails with invalid email format."""
        data = {
            "email": "not-an-email",
            "password": "SecurePassword123!",
        }
        serializer = SignupSerializer(data=data)

        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_weak_password(self):
        """Test validation fails with weak password."""
        data = {
            "email": "test@example.com",
            "password": "123",  # Too short and simple
        }
        serializer = SignupSerializer(data=data)

        assert not serializer.is_valid()
        assert "password" in serializer.errors

    def test_missing_email(self):
        """Test validation fails when email is missing."""
        data = {
            "password": "SecurePassword123!",
        }
        serializer = SignupSerializer(data=data)

        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_missing_password(self):
        """Test validation fails when password is missing."""
        data = {
            "email": "test@example.com",
        }
        serializer = SignupSerializer(data=data)

        assert not serializer.is_valid()
        assert "password" in serializer.errors


class TestSigninSerializer:
    """Test cases for SigninSerializer."""

    def test_valid_data(self):
        """Test serializer with valid data."""
        data = {
            "email": "test@example.com",
            "password": "password123",
        }
        serializer = SigninSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["email"] == data["email"]

    def test_email_normalization(self):
        """Test email is normalized to lowercase."""
        data = {
            "email": "Test@EXAMPLE.COM",
            "password": "password123",
        }
        serializer = SigninSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["email"] == "test@example.com"

    def test_invalid_email_format(self):
        """Test validation fails with invalid email format."""
        data = {
            "email": "not-an-email",
            "password": "password123",
        }
        serializer = SigninSerializer(data=data)

        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_missing_fields(self):
        """Test validation fails when fields are missing."""
        # Missing email
        serializer = SigninSerializer(data={"password": "password"})
        assert not serializer.is_valid()
        assert "email" in serializer.errors

        # Missing password
        serializer = SigninSerializer(data={"email": "test@example.com"})
        assert not serializer.is_valid()
        assert "password" in serializer.errors


class TestTokenRefreshSerializer:
    """Test cases for TokenRefreshSerializer."""

    def test_valid_data(self):
        """Test serializer with valid data."""
        data = {
            "refresh_token": "some-refresh-token",
        }
        serializer = TokenRefreshSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["refresh_token"] == data["refresh_token"]

    def test_missing_refresh_token(self):
        """Test validation fails when refresh_token is missing."""
        serializer = TokenRefreshSerializer(data={})

        assert not serializer.is_valid()
        assert "refresh_token" in serializer.errors
