"""
Tests for rate limiting throttles.
Ensures rate limits are enforced correctly via Redis.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestUserRateThrottle:
    """Test per-user rate throttling."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test client and clear cache before each test."""
        self.client = APIClient()
        cache.clear()
        yield
        cache.clear()

    @pytest.fixture(autouse=True)
    def enable_throttling(self, settings):
        """Enable throttling for these tests and force DRF to reload settings."""
        import sys
        import importlib
        
        # Set throttle classes in settings
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = [
            "apps.auth.throttles.UserRateThrottle",
        ]
        
        # Reload rest_framework.settings module to clear all caches
        if 'rest_framework.settings' in sys.modules:
            importlib.reload(sys.modules['rest_framework.settings'])
        
        # Remove urls module from sys.modules to force reimport
        if 'api.urls' in sys.modules:
            del sys.modules['api.urls']
        
        # Clear Django's URL resolver cache
        from django.urls import clear_url_caches
        clear_url_caches()
        
        # Force reimport of urls to pick up new throttle settings
        import api.urls  # noqa: F401
        
        return settings

    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(
            email="throttle@example.com",
            password="TestPassword123!",
        )

    @pytest.fixture
    def auth_client(self, user):
        """Create an authenticated API client."""
        from apps.auth.services import auth_service

        tokens = auth_service.authenticate_user(
            email="throttle@example.com",
            password="TestPassword123!",
        )
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access_token']}")
        return client

    def test_rate_limit_not_exceeded(self, auth_client, settings):
        """Test that requests under the rate limit succeed."""
        # Override rate limit for testing (using built-in rate limit settings)
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["user"] = "10/hour"

        # Make requests under the limit to authenticated endpoint
        for _ in range(5):
            response = auth_client.get("/api/auth/me")
            assert response.status_code == 200

    def test_rate_limit_exceeded(self, auth_client, settings):
        """Test that requests over the rate limit are blocked with 429."""
        # Set a very low rate limit for testing
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["user"] = "3/hour"

        # Make requests up to the limit to authenticated endpoint
        for _ in range(3):
            response = auth_client.get("/api/auth/me")
            assert response.status_code == 200

        # Next request should be throttled
        response = auth_client.get("/api/auth/me")
        assert response.status_code == 429
        assert "throttled" in response.data["detail"].lower()

    def test_different_users_have_separate_limits(self, settings):
        """Test that rate limits are per-user, not global."""
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["user"] = "2/hour"

        # Create two users
        User.objects.create_user(
            email="user1@example.com",
            password="TestPassword123!",
        )
        User.objects.create_user(
            email="user2@example.com",
            password="TestPassword123!",
        )

        from apps.auth.services import auth_service

        # Get tokens for both users
        tokens1 = auth_service.authenticate_user(
            email="user1@example.com",
            password="TestPassword123!",
        )
        tokens2 = auth_service.authenticate_user(
            email="user2@example.com",
            password="TestPassword123!",
        )

        # Create clients for both users
        client1 = APIClient()
        client1.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens1['access_token']}")

        client2 = APIClient()
        client2.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens2['access_token']}")

        # User1 hits their limit on authenticated endpoint
        for _ in range(2):
            response = client1.get("/api/auth/me")
            assert response.status_code == 200

        response = client1.get("/api/auth/me")
        assert response.status_code == 429

        # User2 should still be able to make requests (separate limit)
        response = client2.get("/api/auth/me")
        assert response.status_code == 200

    def test_unauthenticated_requests_not_throttled_by_user_throttle(self, settings):
        """Test that unauthenticated requests are not subject to user throttle."""
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["user"] = "2/hour"

        client = APIClient()

        # Unauthenticated requests to public endpoints should work
        for _ in range(5):
            response = client.post(
                "/api/auth/signin",
                {"email": "test@example.com", "password": "wrong"},
                format="json",
            )
            # Should get 401 (not throttled), not 429
            assert response.status_code == 401


@pytest.mark.django_db
class TestAnonRateThrottle:
    """Test per-IP rate throttling for anonymous users."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Clear cache before each test."""
        cache.clear()
        yield
        cache.clear()

    def test_anon_throttle_exists(self):
        """Test that AnonRateThrottle class exists and can be imported."""
        from apps.auth.throttles import AnonRateThrottle

        assert AnonRateThrottle is not None
        assert AnonRateThrottle.scope == "anon"
