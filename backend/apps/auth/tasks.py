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

    This is an idempotent task that ensures default categories exist
    for a user. Default categories are created synchronously during
    registration (in AuthService.register_user), so this task acts
    as a safety net — it only creates categories that are missing.

    Args:
        user_id: ID of the user to initialize

    Retries:
        3 times with 60 second delay between retries
    """
    try:
        from django.core.cache import cache

        # Import Category model (avoid circular imports)
        from apps.notes.models import Category

        from apps.auth.services import DEFAULT_CATEGORIES

        user = User.objects.get(id=user_id)
        logger.info(f"Initializing environment for user {user.email} (ID: {user_id})")

        existing_names = set(
            Category.objects.filter(user=user).values_list("name", flat=True)
        )

        created_ids: list[int] = []
        for cat in DEFAULT_CATEGORIES:
            if cat["name"] in existing_names:
                logger.info(
                    f"Default '{cat['name']}' category already exists "
                    f"for user {user.email}, skipping"
                )
                continue

            category = Category.objects.create(
                user=user,
                name=cat["name"],
                color=cat["color"],
            )
            created_ids.append(category.id)

            # Initialize category note count in Redis cache
            cache_key = f"category:{category.id}:note_count"
            cache.set(cache_key, 0, timeout=3600)

            logger.info(
                f"Created default '{cat['name']}' category (ID: {category.id}) "
                f"for user {user.email}"
            )

        logger.info(f"User environment initialization completed for {user.email}")

        return {
            "user_id": user_id,
            "email": user.email,
            "status": "initialized",
            "default_category_ids": created_ids,
        }

    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        raise
    except Exception as exc:
        logger.error(f"Error initializing environment for user {user_id}: {str(exc)}")
        # Retry the task
        raise self.retry(exc=exc) from exc
