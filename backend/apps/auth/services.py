"""
Service Layer for authentication business logic.
All business logic resides here, keeping views and serializers thin.
"""

import logging
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)
User = get_user_model()

# Default categories every new user starts with
DEFAULT_CATEGORIES = [
    {"name": "Random Thoughts", "color": "#6366f1"},
    {"name": "Personal", "color": "#10b981"},
    {"name": "Work", "color": "#f59e0b"},
]


class AuthService:
    """
    Service class for authentication operations.
    Implements Service Layer Pattern.
    """

    @staticmethod
    @transaction.atomic
    def register_user(email: str, password: str) -> dict:
        """
        Register a new user.

        Creates the user account and default categories synchronously
        within the same transaction to guarantee they are always available.

        Args:
            email: User's email address (will be normalized)
            password: User's password (will be hashed)

        Returns:
            Dict containing user data

        Raises:
            ValidationError: If email already exists or validation fails
        """
        from apps.notes.models import Category

        # Normalize email to lowercase
        email = email.lower().strip()

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            raise ValidationError({"email": ["A user with this email already exists."]})

        # Create user with hashed password
        user = User.objects.create_user(
            email=email,
            password=password,
        )

        # Create default categories synchronously within the same
        # transaction so they are guaranteed to exist when the user
        # first loads the dashboard.
        for cat in DEFAULT_CATEGORIES:
            category = Category.objects.create(
                user=user,
                name=cat["name"],
                color=cat["color"],
            )
            # Initialize category note count in cache
            cache_key = f"category:{category.id}:note_count"
            cache.set(cache_key, 0, timeout=3600)

        logger.info(
            f"Created user {user.email} (ID: {user.id}) with "
            f"{len(DEFAULT_CATEGORIES)} default categories"
        )

        return {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at,
        }

    @staticmethod
    def authenticate_user(email: str, password: str) -> dict:
        """
        Authenticate user and generate JWT tokens.

        Args:
            email: User's email address (will be normalized)
            password: User's password

        Returns:
            Dict containing access_token, refresh_token, and token_type

        Raises:
            AuthenticationFailed: If credentials are invalid
        """
        # Normalize email to lowercase
        email = email.lower().strip()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid credentials.") from None

        # Check password
        if not user.check_password(password):
            raise AuthenticationFailed("Invalid credentials.")

        # Check if user is active
        if not user.is_active:
            raise AuthenticationFailed("User account is disabled.")

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "token_type": "Bearer",
        }

    @staticmethod
    def refresh_access_token(refresh_token: str) -> dict:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            Dict containing new access_token, refresh_token (if rotated), and token_type

        Raises:
            AuthenticationFailed: If refresh token is invalid or blacklisted
        """
        try:
            refresh = RefreshToken(refresh_token)

            # Generate new access token
            access_token = str(refresh.access_token)

            # If token rotation is enabled, return new refresh token
            response = {
                "access_token": access_token,
                "token_type": "Bearer",
            }

            # Check if rotation is enabled and include new refresh token
            from django.conf import settings

            if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False):
                response["refresh_token"] = str(refresh)

            return response
        except TokenError as e:
            raise AuthenticationFailed(
                f"Invalid or expired refresh token: {str(e)}"
            ) from e

    @staticmethod
    def logout_user(refresh_token: str) -> None:
        """
        Logout user by blacklisting refresh token in Redis.

        Args:
            refresh_token: Valid refresh token to be blacklisted

        Raises:
            AuthenticationFailed: If refresh token is invalid

        Implementation:
            - Validates the refresh token
            - Extracts JTI (JWT ID) from token
            - Stores JTI in Redis with TTL matching token expiration
            - Key format: blacklist:jti:{jti_value}
            - Future token validation will check this blacklist
        """
        try:
            # Validate and decode the refresh token
            refresh = RefreshToken(refresh_token)

            # Extract JTI (JWT ID) - unique identifier for this token
            jti = refresh.get("jti")
            if not jti:
                raise AuthenticationFailed("Invalid token: missing JTI")

            # Calculate remaining lifetime of the token
            exp_timestamp = refresh.get("exp")
            if not exp_timestamp:
                raise AuthenticationFailed("Invalid token: missing expiration")

            current_timestamp = datetime.now().timestamp()
            remaining_seconds = int(exp_timestamp - current_timestamp)

            # Only blacklist if token is still valid
            if remaining_seconds > 0:
                # Store JTI in Redis with expiration matching token lifetime
                cache_key = f"blacklist:jti:{jti}"
                cache.set(cache_key, "1", timeout=remaining_seconds)

        except TokenError as e:
            raise AuthenticationFailed(
                f"Invalid or expired refresh token: {str(e)}"
            ) from e


# Singleton instance for easy access
auth_service = AuthService()
