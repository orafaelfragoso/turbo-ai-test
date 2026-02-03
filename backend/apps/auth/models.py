"""
User models for authentication.
"""

from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models


class UserManager(DjangoUserManager):
    """
    Custom user manager for email-based authentication.
    Overrides default UserManager to not require username.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        Username is auto-generated from email if not provided.
        """
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        
        # Auto-generate username from email if not provided
        if "username" not in extra_fields:
            base_username = email.split("@")[0]
            username = base_username
            counter = 1
            
            # Ensure username is unique by appending a counter if needed
            while self.model.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            extra_fields["username"] = username

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Uses email as the primary identifier instead of username.
    """

    email = models.EmailField(
        unique=True, db_index=True, help_text="Email address for authentication"
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text="Auto-generated from email, not used for authentication",
    )

    # Additional fields for user profile
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Use email as the USERNAME_FIELD for authentication
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Email is already required as USERNAME_FIELD

    # Use custom manager
    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email
