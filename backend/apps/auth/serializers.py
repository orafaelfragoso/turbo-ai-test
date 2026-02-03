"""
Serializers for authentication endpoints.
Handles validation and data transformation only.
Business logic is in services.py.
"""

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


class SignupSerializer(serializers.Serializer):
    """
    Serializer for user registration.
    Validates email and password input.
    """

    email = serializers.EmailField(
        required=True, help_text="Email address for registration"
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        help_text="Password (min 8 characters, must pass validation)",
    )

    def validate_email(self, value):
        """Validate email format and normalize."""
        return value.lower().strip()

    def validate_password(self, value):
        """Validate password strength using Django's validators."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages)) from e
        return value


class SigninSerializer(serializers.Serializer):
    """
    Serializer for user authentication.
    Validates credentials for signin.
    """

    email = serializers.EmailField(required=True, help_text="Email address")
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        help_text="Password",
    )

    def validate_email(self, value):
        """Normalize email."""
        return value.lower().strip()


class TokenRefreshSerializer(serializers.Serializer):
    """
    Serializer for token refresh.
    Validates refresh token input.
    """

    refresh_token = serializers.CharField(
        required=True, help_text="Refresh token to generate new access token"
    )


class UserSerializer(serializers.Serializer):
    """
    Serializer for user data in responses.
    """

    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class TokenResponseSerializer(serializers.Serializer):
    """
    Serializer for token response.
    """

    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    token_type = serializers.CharField(read_only=True, default="Bearer")


class LogoutSerializer(serializers.Serializer):
    """
    Serializer for logout request.
    Validates refresh token for blacklisting.
    """

    refresh_token = serializers.CharField(
        required=True, help_text="Refresh token to be blacklisted"
    )


class LogoutResponseSerializer(serializers.Serializer):
    """
    Serializer for logout response.
    """

    message = serializers.CharField(read_only=True, default="Successfully logged out")


class ErrorResponseSerializer(serializers.Serializer):
    """
    Serializer for error responses.
    """

    detail = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True, required=False)
