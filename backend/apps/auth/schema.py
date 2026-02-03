"""
OpenAPI schema extensions for authentication.
"""

from drf_spectacular.extensions import OpenApiAuthenticationExtension


class BlacklistCheckingJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    OpenAPI schema extension for BlacklistCheckingJWTAuthentication.
    
    This tells drf-spectacular how to document our custom JWT authentication
    that includes blacklist checking via Redis.
    """

    target_class = "apps.auth.authentication.BlacklistCheckingJWTAuthentication"
    name = "jwtAuth"

    def get_security_definition(self, auto_schema):
        """
        Return the OpenAPI security scheme for JWT authentication.
        
        This is the same as standard JWT but with additional documentation
        about the blacklist checking behavior.
        """
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": (
                "JWT access token for authentication. "
                "Token is validated and checked against Redis blacklist. "
                "Obtain via /api/auth/signin endpoint."
            ),
        }
