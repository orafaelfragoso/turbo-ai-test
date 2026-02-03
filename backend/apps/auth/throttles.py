"""
Custom throttle classes for rate limiting.
Uses Redis backend for distributed rate limiting across multiple servers.
"""

from rest_framework.throttling import UserRateThrottle as DRFUserRateThrottle


class UserRateThrottle(DRFUserRateThrottle):
    """
    Per-user rate throttle for authenticated requests.

    Uses Redis cache backend for distributed rate limiting.
    Rate is configurable via REST_FRAMEWORK settings.

    Default: 100 requests per hour per user.
    """

    scope = "user"

    def get_cache_key(self, request, view):
        """
        Generate cache key for rate limiting.

        Format: throttle_user_{user_id}_{scope}
        """
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            # For unauthenticated users, fall back to IP-based throttling
            ident = self.get_ident(request)

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }


class AnonRateThrottle(DRFUserRateThrottle):
    """
    Per-IP rate throttle for anonymous requests.

    Uses Redis cache backend for distributed rate limiting.
    Useful for protecting public endpoints like signup/signin.

    Default: 20 requests per hour per IP.
    """

    scope = "anon"

    def get_cache_key(self, request, view):
        """
        Generate cache key for anonymous rate limiting.

        Format: throttle_anon_{ip_address}_{scope}
        """
        if request.user and request.user.is_authenticated:
            # Don't throttle authenticated users with anon throttle
            return None

        ident = self.get_ident(request)

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }
