"""
Pytest configuration and fixtures for the entire backend test suite.
"""

import pytest
from django.conf import settings


@pytest.fixture(scope="session", autouse=True)
def configure_test_settings(django_db_setup, django_db_blocker):
    """
    Configure test settings to fix warnings and ensure proper test environment.

    This fixture runs once per test session and configures:
    - A 32+ byte SECRET_KEY to avoid JWT HMAC key length warnings
    - Any other global test configurations
    """
    with django_db_blocker.unblock():
        # Set a proper 32+ byte SECRET_KEY for JWT HMAC
        # (SHA256 requires 32 bytes minimum)
        # This fixes: InsecureKeyLengthWarning from PyJWT
        settings.SECRET_KEY = (
            "test-secret-key-that-is-at-least-32-bytes-long-for-sha256-hmac"
        )
        settings.SIMPLE_JWT["SIGNING_KEY"] = settings.SECRET_KEY


@pytest.fixture
def celery_eager_mode(settings):
    """
    Configure Celery to run tasks synchronously in tests.
    Makes testing async tasks easier by executing them immediately.
    """
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
    return settings


@pytest.fixture(autouse=True)
def disable_throttling(settings, request):
    """
    Disable rate limiting throttles for all tests by default.
    Individual throttle tests can override this by setting rates explicitly.
    Skips disabling for tests in test_throttles.py to allow proper testing.
    """
    # Don't disable throttling for throttle tests
    if "test_throttles" not in str(request.fspath):
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
    return settings
