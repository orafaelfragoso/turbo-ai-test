"""
URL configuration for notes and categories endpoints.
"""

from django.urls import path

from .views import CategoryViewSet, NoteViewSet

app_name = "notes"

urlpatterns = [
    # Category endpoints
    path("categories/", CategoryViewSet.as_view({"get": "list", "post": "create"}), name="category-list"),
    path(
        "categories/<int:pk>/",
        CategoryViewSet.as_view({
            "get": "retrieve",
            "patch": "partial_update",
            "delete": "destroy",
        }),
        name="category-detail",
    ),
    # Note endpoints
    path("notes/", NoteViewSet.as_view({"get": "list", "post": "create"}), name="note-list"),
    path(
        "notes/<uuid:pk>/",
        NoteViewSet.as_view({
            "get": "retrieve",
            "patch": "partial_update",
            "delete": "destroy",
        }),
        name="note-detail",
    ),
]
