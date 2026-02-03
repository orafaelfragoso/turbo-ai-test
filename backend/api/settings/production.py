"""
Production settings.
"""

from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Production security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Logging - production level
LOGGING["root"]["level"] = "WARNING"  # noqa
LOGGING["loggers"]["django"]["level"] = "WARNING"  # noqa
LOGGING["loggers"]["api"]["level"] = "INFO"  # noqa
LOGGING["loggers"]["apps"]["level"] = "INFO"  # noqa

# Database optimizations for PostgreSQL JSONB
DATABASES["default"]["OPTIONS"] = {  # noqa
    "connect_timeout": 10,
}
DATABASES["default"]["CONN_MAX_AGE"] = 600  # noqa

# Gunicorn worker configuration (set via environment variables)
# GUNICORN_WORKERS and GUNICORN_THREADS are read from environment

# Email backend for production (configure with your email service)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
# EMAIL_PORT = env('EMAIL_PORT', default=587)
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
# EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')

# Static files configuration for production
# Consider using WhiteNoise or cloud storage (S3, GCS)
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
