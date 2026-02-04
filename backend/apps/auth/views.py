"""
Thin API views for authentication endpoints.
Views parse requests, call services, and return responses.
Business logic is in services.py.
"""

from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    ErrorResponseSerializer,
    LogoutResponseSerializer,
    LogoutSerializer,
    SigninSerializer,
    SignupSerializer,
    TokenRefreshSerializer,
    TokenResponseSerializer,
    UserSerializer,
)
from .services import auth_service


@extend_schema_view(
    post=extend_schema(
        tags=["auth"],
        summary="User Registration",
        description="Register a new user account with email and password. "
        "Triggers background task for user environment initialization. "
        "This endpoint is public and does not require authentication.",
        request=SignupSerializer,
        responses={
            201: UserSerializer,
            400: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                name="Successful Registration",
                value={
                    "id": 1,
                    "email": "user@example.com",
                    "created_at": "2024-01-01T12:00:00Z",
                },
                response_only=True,
            )
        ],
        auth=[],  # Public endpoint - no authentication required
    )
)
class SignupView(APIView):
    """
    User registration endpoint.
    POST /api/auth/signup

    Accepts email and password.
    Returns user data (no tokens on signup).
    Triggers background task for user environment initialization.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Register a new user."""
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call service layer
        user_data = auth_service.register_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        return Response(user_data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    post=extend_schema(
        tags=["auth"],
        summary="User Sign-In",
        description="Authenticate user with email and password. "
        "Returns JWT access token (15 min) and refresh token (7 days). "
        "This endpoint is public and does not require authentication.",
        request=SigninSerializer,
        responses={
            200: TokenResponseSerializer,
            401: ErrorResponseSerializer,
            429: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                name="Successful Authentication",
                value={
                    "access_token": "eyJ0eXAiOiJKV1Qi...",
                    "refresh_token": "eyJ0eXAiOiJKV1Qi...",
                    "token_type": "Bearer",
                },
                response_only=True,
            )
        ],
        auth=[],  # Public endpoint - no authentication required
    )
)
class SigninView(APIView):
    """
    User authentication endpoint.
    POST /api/auth/signin

    Accepts email and password.
    Returns access_token (short-lived) and refresh_token (long-lived).
    OAuth2-compliant JWT format.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticate user and generate JWT tokens."""
        serializer = SigninSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call service layer
        tokens = auth_service.authenticate_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        return Response(tokens, status=status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(
        tags=["auth"],
        summary="Refresh Access Token",
        description="Generate a new access token using a valid refresh token. "
        "Validates token is not blacklisted in Redis. "
        "Returns new refresh token if rotation is enabled. "
        "This endpoint is public per OAuth2 specification (no Bearer token required).",
        request=TokenRefreshSerializer,
        responses={
            200: TokenResponseSerializer,
            401: ErrorResponseSerializer,
            429: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                name="Successful Token Refresh",
                value={
                    "access_token": "eyJ0eXAiOiJKV1Qi...",
                    "refresh_token": "eyJ0eXAiOiJKV1Qi...",
                    "token_type": "Bearer",
                },
                response_only=True,
            )
        ],
        auth=[],  # Public endpoint - no authentication required (OAuth2 standard)
    )
)
class TokenRefreshView(APIView):
    """
    Token refresh endpoint.
    POST /api/auth/refresh

    Accepts refresh_token.
    Returns new access_token.
    Validates token against denylist in Redis.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Refresh access token."""
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call service layer
        tokens = auth_service.refresh_access_token(
            refresh_token=serializer.validated_data["refresh_token"],
        )

        return Response(tokens, status=status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(
        tags=["auth"],
        summary="User Logout",
        description="Logout user by blacklisting refresh token in Redis. "
        "Requires authentication. Token cannot be reused after logout.",
        request=LogoutSerializer,
        responses={
            200: LogoutResponseSerializer,
            401: ErrorResponseSerializer,
            429: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                name="Successful Logout",
                value={"message": "Successfully logged out"},
                response_only=True,
            )
        ],
    )
)
class LogoutView(APIView):
    """
    User logout endpoint.
    POST /api/auth/logout

    Requires authentication.
    Accepts refresh_token.
    Blacklists token in Redis to prevent reuse.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Logout user and blacklist refresh token."""
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call service layer
        auth_service.logout_user(
            refresh_token=serializer.validated_data["refresh_token"],
        )

        return Response(
            {"message": "Successfully logged out"}, status=status.HTTP_200_OK
        )


@extend_schema_view(
    get=extend_schema(
        tags=["auth"],
        summary="Get Current User",
        description="Get information about the currently authenticated user.",
        responses={
            200: UserSerializer,
            401: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                name="Current User Info",
                value={
                    "id": 1,
                    "email": "user@example.com",
                    "created_at": "2024-01-01T12:00:00Z",
                },
                response_only=True,
            )
        ],
    )
)
class MeView(APIView):
    """
    Get current user endpoint.
    GET /api/auth/me
    
    Requires authentication.
    Returns information about the currently authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get_throttles(self):
        """
        Dynamically get throttle instances from current api_settings.
        This allows tests to modify throttle settings and have them take effect.
        """
        from rest_framework.settings import api_settings
        throttle_classes = api_settings.DEFAULT_THROTTLE_CLASSES
        return [throttle() for throttle in throttle_classes]

    def get(self, request):
        """Get current user information."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
