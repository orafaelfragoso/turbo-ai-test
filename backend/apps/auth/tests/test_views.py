"""
Integration tests for authentication API views.
Tests HTTP endpoints, status codes, and response formats.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.fixture
def test_user_data():
    """Fixture for test user data."""
    return {
        "email": "testuser@example.com",
        "password": "SecureTestPassword123!",
    }


@pytest.mark.django_db
class TestSignupView:
    """Test cases for signup endpoint."""

    def test_signup_success(self, api_client, test_user_data):
        """Test successful user signup."""
        url = reverse("auth:signup")
        response = api_client.post(url, test_user_data, format="json")

        assert response.status_code == 201
        assert "id" in response.data
        assert response.data["email"] == test_user_data["email"]
        assert "password" not in response.data  # Password should not be in response

    def test_signup_duplicate_email(self, api_client, test_user_data):
        """Test signup with duplicate email returns 400."""
        url = reverse("auth:signup")

        # Create first user
        api_client.post(url, test_user_data, format="json")

        # Attempt duplicate
        response = api_client.post(url, test_user_data, format="json")

        assert response.status_code == 400
        assert "email" in str(response.data).lower()

    def test_signup_invalid_email(self, api_client):
        """Test signup with invalid email returns 400."""
        url = reverse("auth:signup")
        data = {
            "email": "not-an-email",
            "password": "SecurePassword123!",
        }
        response = api_client.post(url, data, format="json")

        assert response.status_code == 400
        assert "email" in str(response.data).lower()

    def test_signup_weak_password(self, api_client):
        """Test signup with weak password returns 400."""
        url = reverse("auth:signup")
        data = {
            "email": "test@example.com",
            "password": "123",  # Too weak
        }
        response = api_client.post(url, data, format="json")

        assert response.status_code == 400
        assert "password" in str(response.data).lower()

    def test_signup_missing_fields(self, api_client):
        """Test signup with missing fields returns 400."""
        url = reverse("auth:signup")

        # Missing password
        response = api_client.post(url, {"email": "test@example.com"}, format="json")
        assert response.status_code == 400

        # Missing email
        response = api_client.post(
            url, {"password": "SecurePassword123!"}, format="json"
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestSigninView:
    """Test cases for signin endpoint."""

    def test_signin_success(self, api_client, test_user_data):
        """Test successful user signin."""
        # Create user first
        signup_url = reverse("auth:signup")
        api_client.post(signup_url, test_user_data, format="json")

        # Sign in
        signin_url = reverse("auth:signin")
        response = api_client.post(signin_url, test_user_data, format="json")

        assert response.status_code == 200
        assert "access_token" in response.data
        assert "refresh_token" in response.data
        assert response.data["token_type"] == "Bearer"

    def test_signin_invalid_credentials(self, api_client, test_user_data):
        """Test signin with invalid credentials returns 401."""
        # Create user first
        signup_url = reverse("auth:signup")
        api_client.post(signup_url, test_user_data, format="json")

        # Attempt signin with wrong password
        signin_url = reverse("auth:signin")
        invalid_data = {
            "email": test_user_data["email"],
            "password": "WrongPassword123!",
        }
        response = api_client.post(signin_url, invalid_data, format="json")

        assert response.status_code == 401

    def test_signin_nonexistent_user(self, api_client):
        """Test signin with non-existent user returns 401."""
        signin_url = reverse("auth:signin")
        data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!",
        }
        response = api_client.post(signin_url, data, format="json")

        assert response.status_code == 401

    def test_signin_missing_fields(self, api_client):
        """Test signin with missing fields returns 400."""
        signin_url = reverse("auth:signin")

        # Missing password
        response = api_client.post(
            signin_url, {"email": "test@example.com"}, format="json"
        )
        assert response.status_code == 400

        # Missing email
        response = api_client.post(signin_url, {"password": "password"}, format="json")
        assert response.status_code == 400


@pytest.mark.django_db
class TestTokenRefreshView:
    """Test cases for token refresh endpoint."""

    def test_refresh_token_success(self, api_client, test_user_data):
        """Test successful token refresh."""
        # Create user and sign in
        signup_url = reverse("auth:signup")
        api_client.post(signup_url, test_user_data, format="json")

        signin_url = reverse("auth:signin")
        signin_response = api_client.post(signin_url, test_user_data, format="json")
        refresh_token = signin_response.data["refresh_token"]

        # Refresh token
        refresh_url = reverse("auth:refresh")
        response = api_client.post(
            refresh_url, {"refresh_token": refresh_token}, format="json"
        )

        assert response.status_code == 200
        assert "access_token" in response.data
        assert response.data["token_type"] == "Bearer"

    def test_refresh_token_invalid(self, api_client):
        """Test refresh with invalid token returns 401."""
        refresh_url = reverse("auth:refresh")
        response = api_client.post(
            refresh_url, {"refresh_token": "invalid-token"}, format="json"
        )

        assert response.status_code == 401

    def test_refresh_token_missing(self, api_client):
        """Test refresh without token returns 400."""
        refresh_url = reverse("auth:refresh")
        response = api_client.post(refresh_url, {}, format="json")

        assert response.status_code == 400
