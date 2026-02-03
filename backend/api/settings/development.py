"""
Development settings.
"""

from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allow all hosts in development
if not ALLOWED_HOSTS:  # noqa
    ALLOWED_HOSTS = ["*"]  # noqa

# Development-specific logging
LOGGING["loggers"]["django"]["level"] = "DEBUG"  # noqa
LOGGING["loggers"]["api"]["level"] = "DEBUG"  # noqa
LOGGING["loggers"]["apps"]["level"] = "DEBUG"  # noqa

# Suppress template variable resolution warnings (harmless noise from drf-spectacular)
LOGGING["loggers"]["django.template"] = {  # noqa
    "handlers": ["console"],
    "level": "INFO",  # Filter out DEBUG warnings about missing template variables
    "propagate": False,
}

# Django Debug Toolbar (optional, uncomment to enable)
# INSTALLED_APPS += ['debug_toolbar']  # noqa
# MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa
# INTERNAL_IPS = ['127.0.0.1']

# CORS - Allow all origins in development (optional, be careful)
# CORS_ALLOW_ALL_ORIGINS = True

# Disable HTTPS redirects in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Email backend for development (console)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
