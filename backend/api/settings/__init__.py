"""
Settings module initialization.
"""

import os

# Determine which settings to use based on DJANGO_SETTINGS_MODULE
settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "api.settings.development")

if "production" in settings_module:
    from .production import *  # noqa
elif "development" in settings_module:
    from .development import *  # noqa
else:
    from .base import *  # noqa
