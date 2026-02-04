"""
Celery background tasks for authentication app.
"""

import logging

from celery import shared_task
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def initialize_user_environment(self, user_id: int):
    """
    Initialize user environment after registration.

    This is an asynchronous task triggered after user signup.
    Creates user-specific data structures, default configurations,
    and initializes the user workspace/environment.

    Args:
        user_id: ID of the user to initialize

    Retries:
        3 times with 60 second delay between retries
    """
    try:
        from django.core.cache import cache

        user = User.objects.get(id=user_id)
        logger.info(f"Initializing environment for user {user.email} (ID: {user_id})")

        # Import Category model (avoid circular imports)
        from apps.notes.models import Category

        # Create default "Random Thoughts" category
        default_category = Category.objects.create(
            user=user,
            name="Random Thoughts",
            color="#6366f1",  # Default indigo color
        )

        # Initialize category note count in Redis cache
        cache_key = f"category:{default_category.id}:note_count"
        cache.set(cache_key, 0, timeout=3600)

        logger.info(
            f"Created default 'Random Thoughts' category (ID: {default_category.id}) "
            f"for user {user.email}"
        )

        logger.info(f"User environment initialization completed for {user.email}")

        return {
            "user_id": user_id,
            "email": user.email,
            "status": "initialized",
            "default_category_id": default_category.id,
        }

    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        raise
    except Exception as exc:
        logger.error(f"Error initializing environment for user {user_id}: {str(exc)}")
        # Retry the task
        raise self.retry(exc=exc) from exc
