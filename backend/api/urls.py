"""
URL configuration for api project.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.utils import OpenApiExample, extend_schema
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckResponseSerializer(serializers.Serializer):
    """Serializer for health check response."""

    status = serializers.CharField(help_text="Health status of the service")


class HealthCheckView(APIView):
    """
    Health check endpoint for Docker health checks and service monitoring.
    
    This endpoint is completely public - no authentication or authorization required.
    Other services can freely check the health status without providing credentials.
    """

    authentication_classes = []  # No authentication - truly public endpoint
    permission_classes = [AllowAny]
    throttle_classes = []  # No throttling for health checks

    @extend_schema(
        summary="Health Check",
        description="Check if the API service is running and healthy. "
        "Returns a 200 status with 'healthy' message when service is operational.",
        responses={
            200: HealthCheckResponseSerializer,
        },
        examples=[
            OpenApiExample(
                name="Healthy Response",
                value={"status": "healthy"},
                response_only=True,
            )
        ],
        tags=["monitoring"],
    )
    def get(self, request):
        """Return health status."""
        return Response({"status": "healthy"}, status=status.HTTP_200_OK)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", HealthCheckView.as_view(), name="health_check"),
    path("api/auth/", include("apps.auth.urls")),
    # OpenAPI/Swagger Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
