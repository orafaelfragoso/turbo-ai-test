"""
Views for notes and categories API endpoints.
Uses ViewSets with thin controller logic - all business logic is in services.py.
"""

from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.auth.authentication import BlacklistCheckingJWTAuthentication
from apps.auth.throttles import UserRateThrottle

from .serializers import (
    CategoryDetailSerializer,
    CategoryListSerializer,
    CategorySerializer,
    NoteCreateSerializer,
    NoteDetailSerializer,
    NoteListSerializer,
    NoteUpdateSerializer,
)
from .services import category_service, note_service


@extend_schema_view(
    list=extend_schema(
        summary="List Categories",
        description="List all categories for the authenticated user with note counts.",
        tags=["categories"],
        responses={200: CategoryListSerializer(many=True)},
    ),
    create=extend_schema(
        summary="Create Category",
        description="Create a new category for the authenticated user.",
        tags=["categories"],
        request=CategorySerializer,
        responses={201: CategoryDetailSerializer},
    ),
    retrieve=extend_schema(
        summary="Get Category",
        description="Retrieve a single category by ID.",
        tags=["categories"],
        responses={200: CategoryDetailSerializer},
    ),
    partial_update=extend_schema(
        summary="Update Category",
        description="Update a category (partial update supported).",
        tags=["categories"],
        request=CategorySerializer,
        responses={200: CategoryDetailSerializer},
    ),
    destroy=extend_schema(
        summary="Delete Category",
        description="Delete a category. Cannot delete 'Random Thoughts' category.",
        tags=["categories"],
        responses={204: None},
    ),
)
class CategoryViewSet(viewsets.ViewSet):
    """
    ViewSet for category CRUD operations.
    All business logic is delegated to CategoryService.
    """

    authentication_classes = [BlacklistCheckingJWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def list(self, request):
        """List all categories for the authenticated user."""
        categories = category_service.list_categories(request.user)
        serializer = CategoryListSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """Create a new category."""
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        category = category_service.create_category(
            request.user, serializer.validated_data
        )

        response_serializer = CategoryDetailSerializer(category)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Retrieve a single category."""
        category = category_service.get_category(request.user, pk)
        serializer = CategoryDetailSerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        """Update a category (partial update)."""
        serializer = CategorySerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        category = category_service.update_category(
            request.user, pk, serializer.validated_data
        )

        response_serializer = CategoryDetailSerializer(category)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """Delete a category."""
        category_service.delete_category(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(
        summary="List Notes",
        description="List all notes for the authenticated user with optional filtering and search.",
        tags=["notes"],
        parameters=[
            OpenApiParameter(
                name="category_id",
                description="Filter by category ID",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="search",
                description="Search in title and content (case-insensitive)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="page",
                description="Page number for pagination",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="page_size",
                description="Number of items per page (max 100)",
                required=False,
                type=int,
            ),
        ],
        responses={200: NoteListSerializer(many=True)},
    ),
    create=extend_schema(
        summary="Create Note",
        description="Create a new note. If no category is specified, defaults to 'Random Thoughts'.",
        tags=["notes"],
        request=NoteCreateSerializer,
        responses={201: NoteDetailSerializer},
    ),
    retrieve=extend_schema(
        summary="Get Note",
        description="Retrieve a single note by UUID.",
        tags=["notes"],
        responses={200: NoteDetailSerializer},
    ),
    partial_update=extend_schema(
        summary="Update Note",
        description="Update a note (partial update supported). Auto-save implementation.",
        tags=["notes"],
        request=NoteUpdateSerializer,
        responses={200: NoteDetailSerializer},
    ),
    destroy=extend_schema(
        summary="Delete Note",
        description="Delete a note.",
        tags=["notes"],
        responses={204: None},
    ),
)
class NoteViewSet(viewsets.ViewSet):
    """
    ViewSet for note CRUD operations.
    All business logic is delegated to NoteService.
    """

    authentication_classes = [BlacklistCheckingJWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def list(self, request):
        """List all notes for the authenticated user with filtering."""
        filters = {
            "category_id": request.query_params.get("category_id"),
            "search": request.query_params.get("search"),
        }

        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}

        notes = note_service.list_notes(request.user, filters)

        # Apply pagination
        from rest_framework.pagination import PageNumberPagination

        paginator = PageNumberPagination()
        paginator.page_size = min(
            int(request.query_params.get("page_size", 20)), 100
        )
        page = paginator.paginate_queryset(notes, request)

        if page is not None:
            serializer = NoteListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = NoteListSerializer(notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """Create a new note."""
        serializer = NoteCreateSerializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)

        note = note_service.create_note(request.user, serializer.validated_data)

        response_serializer = NoteDetailSerializer(note)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Retrieve a single note."""
        note = note_service.get_note(request.user, pk)
        serializer = NoteDetailSerializer(note)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        """Update a note (partial update)."""
        serializer = NoteUpdateSerializer(
            data=request.data, partial=True, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)

        note = note_service.update_note(request.user, pk, serializer.validated_data)

        response_serializer = NoteDetailSerializer(note)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """Delete a note."""
        note_service.delete_note(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
