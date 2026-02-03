"""
Tests for API versioning.
Ensures Accept header versioning works correctly.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestAPIVersioning:
    """Test Accept header-based API versioning."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test client."""
        self.client = APIClient()

    def test_request_with_v1_accept_header(self):
        """Test that v1 version header is accepted."""
        response = self.client.get(
            "/api/health/",
            HTTP_ACCEPT="application/vnd.noteapp.v1+json",
        )
        assert response.status_code == 200

    def test_request_without_version_uses_default(self):
        """Test that requests without version header use default (v1)."""
        response = self.client.get("/api/health/")
        assert response.status_code == 200

    def test_request_with_standard_json_accept_header(self):
        """Test that standard JSON accept header works."""
        response = self.client.get(
            "/api/health/",
            HTTP_ACCEPT="application/json",
        )
        assert response.status_code == 200

    def test_signup_with_versioned_header(self):
        """Test signup endpoint with versioned Accept header."""
        response = self.client.post(
            "/api/auth/signup",
            {
                "email": "versioned@example.com",
                "password": "TestPassword123!",
            },
            format="json",
            HTTP_ACCEPT="application/vnd.noteapp.v1+json",
        )
        assert response.status_code == 201
        assert "email" in response.data

    def test_signin_with_versioned_header(self):
        """Test signin endpoint with versioned Accept header."""
        # Create user first
        User.objects.create_user(
            email="signin@example.com",
            password="TestPassword123!",
        )

        response = self.client.post(
            "/api/auth/signin",
            {
                "email": "signin@example.com",
                "password": "TestPassword123!",
            },
            format="json",
            HTTP_ACCEPT="application/vnd.noteapp.v1+json",
        )
        assert response.status_code == 200
        assert "access_token" in response.data
        assert "refresh_token" in response.data

    def test_versioning_configuration_in_settings(self, settings):
        """Test that versioning is properly configured in settings."""
        assert (
            settings.REST_FRAMEWORK["DEFAULT_VERSIONING_CLASS"]
            == "rest_framework.versioning.AcceptHeaderVersioning"
        )
        assert settings.REST_FRAMEWORK["DEFAULT_VERSION"] == "v1"
        assert "v1" in settings.REST_FRAMEWORK["ALLOWED_VERSIONS"]


@pytest.mark.django_db
class TestVersioningIntegration:
    """Integration tests for API versioning across endpoints."""

    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(
            email="version_test@example.com",
            password="TestPassword123!",
        )

    @pytest.fixture
    def auth_client(self, user):
        """Create an authenticated API client with versioned headers."""
        from apps.auth.services import auth_service

        tokens = auth_service.authenticate_user(
            email="version_test@example.com",
            password="TestPassword123!",
        )
        client = APIClient()
        client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {tokens['access_token']}",
            HTTP_ACCEPT="application/vnd.noteapp.v1+json",
        )
        return client

    def test_authenticated_request_with_version_header(self, auth_client):
        """Test that authenticated requests work with version header."""
        response = auth_client.get("/api/health/")
        assert response.status_code == 200

    def test_all_auth_endpoints_support_versioning(self, user):
        """Test that all auth endpoints work with versioned headers."""
        client = APIClient()
        headers = {"HTTP_ACCEPT": "application/vnd.noteapp.v1+json"}

        # Signup
        signup_response = client.post(
            "/api/auth/signup",
            {"email": "newuser@example.com", "password": "TestPassword123!"},
            format="json",
            **headers,
        )
        assert signup_response.status_code == 201

        # Signin
        signin_response = client.post(
            "/api/auth/signin",
            {"email": user.email, "password": "TestPassword123!"},
            format="json",
            **headers,
        )
        assert signin_response.status_code == 200
        tokens = signin_response.data

        # Refresh
        refresh_response = client.post(
            "/api/auth/refresh",
            {"refresh_token": tokens["refresh_token"]},
            format="json",
            **headers,
        )
        assert refresh_response.status_code == 200

        # Logout
        auth_client = APIClient()
        auth_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {tokens['access_token']}",
            HTTP_ACCEPT="application/vnd.noteapp.v1+json",
        )
        logout_response = auth_client.post(
            "/api/auth/logout",
            {"refresh_token": tokens["refresh_token"]},
            format="json",
        )
        assert logout_response.status_code == 200
