"""
Custom authentication backends with token blacklist checking.
"""

from django.core.cache import cache
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class BlacklistCheckingJWTAuthentication(JWTAuthentication):
    """
    JWT Authentication with Redis blacklist checking.

    Extends the default JWTAuthentication to check if the token's JTI
    is blacklisted in Redis before allowing access.
    """

    def authenticate(self, request):
        """
        Authenticate the request and check token blacklist.

        Returns:
            Tuple of (user, validated_token) if authentication succeeds
            None if no token provided

        Raises:
            AuthenticationFailed: If token is blacklisted or invalid
        """
        # Call parent authentication
        result = super().authenticate(request)

        if result is None:
            # No token provided - let permission classes handle it
            return None

        user, validated_token = result

        # Extract JTI from token
        jti = validated_token.get("jti")

        if jti:
            # Check if token is blacklisted
            cache_key = f"blacklist:jti:{jti}"
            if cache.get(cache_key):
                raise AuthenticationFailed("Token has been revoked")

        return user, validated_token
