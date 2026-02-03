# Backend Technical Spec: Notes Management Service

## 1. Architectural Strategy

The "Notes" feature is implemented using a **Service-Layer Pattern**. This decouples the REST interface (Controllers/Views) from the persistence logic, allowing for easier unit testing and future integration with asynchronous workers (e.g., Celery for category count synchronization).

The architecture follows a strict separation of concerns:
- **Views** (`views.py`): Handle HTTP requests/responses, delegate to service layer
- **Serializers** (`serializers.py`): Validate and transform request/response data
- **Services** (`services.py`): Contain all business logic (note creation, updates, category management)
- **Models** (`models.py`): Database schema definitions for Note and Category
- **Tasks** (`tasks.py`): Celery background tasks (e.g., category count synchronization)

## 2. Data Schema & Persistence (PostgreSQL)

The database layer is optimized for write-heavy workloads (auto-saving) and efficient filtered reads. Both Note and Category models implement multi-tenant isolation via `user_id` foreign keys.

### 2.1 Category Model

Categories are user-defined organizational containers for notes. **Each user has their own isolated set of categories** - category names are unique within a user's scope, not globally. Multiple users can have categories with the same name (e.g., "Work", "Personal") without conflicts.

| Field | Type | Storage Strategy | Notes |
| --- | --- | --- | --- |
| `id` | `BigInt` | Primary Key | Auto-incrementing integer ID. |
| `user_id` | `BigInt` | Indexed FK | Direct relation to the Auth User. Composite index with `name` for uniqueness. |
| `name` | `Varchar(100)` | Indexed (composite) | Category name. Unique per user (composite unique constraint with user_id). |
| `color` | `CharField(7)` | Default: `#6366f1` | Hex color code for UI display (e.g., `#6366f1`). Validated to be valid hex color. |
| `created_at` | `Timestamptz` | Auto-created | Timestamp of category creation. |
| `updated_at` | `Timestamptz` | Auto-updated | Timestamp of last category update. |

**Key Design Decisions:**
- **Categories are scoped per user** - the composite unique constraint on `(user_id, name)` ensures category names are unique within each user's scope, not globally across the application
- Default category "Random Thoughts" is created automatically for each user during environment initialization
- Color field allows UI customization (default indigo color)
- Category deletion sets notes' `category_id` to `NULL` (SET_NULL) to prevent data loss

**Database Indexes:**
- Primary key on `id`
- Foreign key index on `user_id`
- Composite unique constraint on `(user_id, name)`
- Index on `user_id` for efficient user-scoped queries

### 2.2 Note Model

Notes are the core content entities, organized into categories.

| Field | Type | Storage Strategy | Notes |
| --- | --- | --- | --- |
| `id` | `UUID` | Primary Key | Uses `uuid_generate_v4()` for non-enumerable IDs. Prevents ID enumeration attacks. |
| `user_id` | `BigInt` | Indexed FK | Direct relation to the Auth User. Composite index with `updated_at` for efficient sorting. |
| `category_id` | `BigInt` | Indexed FK (nullable) | Foreign key to Category. `SET_NULL` on delete to prevent note loss. |
| `title` | `Varchar(255)` | B-Tree Index | Note title. Supports prefix searches via B-tree index. |
| `content` | `Text` | TOAST | Note content. Optimized for large text blocks via PostgreSQL TOAST (The Oversized-Attribute Storage Technique). |
| `created_at` | `Timestamptz` | Auto-created | Timestamp of note creation. |
| `updated_at` | `Timestamptz` | Indexed (composite) | Timestamp of last note update. Critical for sorting "Recent" notes. Composite index with `user_id`. |

**Key Design Decisions:**
- UUID primary keys prevent ID enumeration (users cannot guess other users' note IDs)
- `category_id` is nullable to support uncategorized notes
- `updated_at` is automatically updated on every save (Django's `auto_now=True`)
- Content uses PostgreSQL TOAST for efficient storage of large text (>2KB)

**Database Indexes:**
- Primary key on `id` (UUID)
- Foreign key index on `user_id`
- Foreign key index on `category_id`
- B-tree index on `title` for prefix searches
- Composite index on `(user_id, updated_at)` for efficient "recent notes" queries
- Index on `updated_at` for sorting

**Database Constraints:**
- Foreign key constraint: `category_id` references `categories(id)` ON DELETE SET NULL
- Foreign key constraint: `user_id` references `users(id)` ON DELETE CASCADE
- Check constraint: `title` length <= 255 characters
- Check constraint: `content` length <= 100,000 characters

## 3. API Contract & Implementation Details

### 3.1 Endpoint Architecture

All endpoints require a valid **JWT Access Token** in the `Authorization: Bearer` header. Authentication is handled by the `BlacklistCheckingJWTAuthentication` backend, which validates tokens and checks the Redis blacklist for revoked tokens.

**API Versioning:** Notes endpoints support Accept header versioning (`Accept: application/vnd.noteapp.v1+json`) consistent with the authentication API, but also accept standard `application/json` for backward compatibility.

**Base URL:** `/api/notes/` and `/api/categories/`

### 3.2 Category Endpoints

#### `GET /api/categories/` (List Categories)

* **Permission:** Authenticated (requires valid JWT)
* **Query Parameters:** None
* **Service Layer:** `category_service.list_categories(user)`
* **Business Logic:**
  1. Query all categories for the authenticated user
  2. Order by `created_at` ascending (oldest first)
  3. Include note count for each category (from Redis cache or database)
* **Response:** `200 OK` with array of categories:
  ```json
  [
    {
      "id": 1,
      "name": "Random Thoughts",
      "color": "#6366f1",
      "note_count": 5,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ]
  ```
* **Error Responses:**
  - `401 Unauthorized`: Missing or invalid access token
  - `429 Too Many Requests`: Rate limit exceeded

#### `POST /api/categories/` (Create Category)

* **Permission:** Authenticated (requires valid JWT)
* **Input Validation:**
  - `name`: Required string, 1-100 characters, unique per user
  - `color`: Optional string, valid hex color code (default: `#6366f1`)
* **Service Layer:** `category_service.create_category(user, data)`
* **Business Logic:**
  1. Validate name is not empty and <= 100 characters
  2. Validate color is valid hex code (7 characters, starts with #)
  3. Check for existing category with same name for this user (raises `ValidationError` if exists)
  4. Create category with user_id from authenticated user
  5. Initialize category note count in Redis cache to 0
* **Response:** `201 Created` with category data:
  ```json
  {
    "id": 1,
    "name": "Work",
    "color": "#10b981",
    "note_count": 0,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
  ```
* **Error Responses:**
  - `400 Bad Request`: Invalid name or color, duplicate category name
  - `401 Unauthorized`: Missing or invalid access token
  - `429 Too Many Requests`: Rate limit exceeded

#### `GET /api/categories/{id}/` (Get Category)

* **Permission:** Authenticated (requires valid JWT)
* **Service Layer:** `category_service.get_category(user, category_id)`
* **Business Logic:**
  1. Query category by ID and user_id
  2. Return 404 if category doesn't exist or belongs to another user
  3. Include note count from Redis cache
* **Response:** `200 OK` with category data (same format as POST response)
* **Error Responses:**
  - `404 Not Found`: Category doesn't exist or belongs to another user
  - `401 Unauthorized`: Missing or invalid access token
  - `429 Too Many Requests`: Rate limit exceeded

#### `PATCH /api/categories/{id}/` (Update Category)

* **Permission:** Authenticated (requires valid JWT)
* **Input Validation:**
  - `name`: Optional string, 1-100 characters, unique per user (if provided)
  - `color`: Optional string, valid hex color code (if provided)
* **Service Layer:** `category_service.update_category(user, category_id, data)`
* **Business Logic:**
  1. Query category by ID and user_id (raises `NotFound` if not found)
  2. If name provided: validate uniqueness per user (excluding current category)
  3. If color provided: validate hex color format
  4. Update only provided fields (partial update)
  5. Update `updated_at` timestamp
* **Response:** `200 OK` with updated category data
* **Error Responses:**
  - `400 Bad Request`: Invalid name or color, duplicate category name
  - `404 Not Found`: Category doesn't exist or belongs to another user
  - `401 Unauthorized`: Missing or invalid access token
  - `429 Too Many Requests`: Rate limit exceeded

#### `DELETE /api/categories/{id}/` (Delete Category)

* **Permission:** Authenticated (requires valid JWT)
* **Service Layer:** `category_service.delete_category(user, category_id)`
* **Business Logic:**
  1. Query category by ID and user_id (raises `NotFound` if not found)
  2. Prevent deletion of "Random Thoughts" category (raises `ValidationError`)
  3. Update all notes in this category to set `category_id = NULL` (transaction-wrapped)
  4. Delete category from database
  5. Remove category note count from Redis cache
  6. Decrement user's total note count in cache (if applicable)
* **Response:** `204 No Content` (empty body)
* **Error Responses:**
  - `400 Bad Request`: Attempting to delete "Random Thoughts" category
  - `404 Not Found`: Category doesn't exist or belongs to another user
  - `401 Unauthorized`: Missing or invalid access token
  - `429 Too Many Requests`: Rate limit exceeded

### 3.3 Note Endpoints

#### `POST /api/notes/` (Create Note - "Draft" Pattern)

* **Permission:** Authenticated (requires valid JWT)
* **Input Validation:**
  - `title`: Optional string, max 255 characters (default: empty string)
  - `content`: Optional string, max 100,000 characters (default: empty string)
  - `category_id`: Optional integer, must belong to user (default: "Random Thoughts" category)
* **Service Layer:** `note_service.create_note(user, data)`
* **Business Logic:**
  1. If `category_id` omitted, query user's "Random Thoughts" category
  2. If "Random Thoughts" doesn't exist (rare), fall back to most recently created category for user
  3. If no categories exist (edge case), create note with `category_id = NULL`
  4. Validate `category_id` belongs to user (if provided)
  5. Create note with UUID primary key
  6. Increment category note count in Redis cache
  7. Set `created_at` and `updated_at` to current timestamp
* **Response:** `201 Created` with note data:
  ```json
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "",
    "content": "",
    "category": {
      "id": 1,
      "name": "Random Thoughts",
      "color": "#6366f1"
    },
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
  ```
* **Error Responses:**
  - `400 Bad Request`: Invalid category_id (doesn't belong to user), title/content too long
  - `401 Unauthorized`: Missing or invalid access token
  - `429 Too Many Requests`: Rate limit exceeded

#### `GET /api/notes/` (List Notes)

* **Permission:** Authenticated (requires valid JWT)
* **Query Parameters:**
  - `category_id` (optional): Filter by category ID
  - `search` (optional): Search in title and content (case-insensitive)
  - `page` (optional): Page number for pagination (default: 1)
  - `page_size` (optional): Items per page (default: 20, max: 100)
* **Service Layer:** `note_service.list_notes(user, filters)`
* **Business Logic:**
  1. Start with queryset filtered by `user_id`
  2. If `category_id` provided: filter by category (validate category belongs to user)
  3. If `search` provided: filter using `Q(title__icontains=search) | Q(content__icontains=search)`
  4. Order by `-updated_at` (most recently updated first)
  5. Use `.select_related('category')` to avoid N+1 queries
  6. Apply pagination (DRF's PageNumberPagination)
  7. Use `NoteListSerializer` which includes `content_preview` (first 200 chars)
* **Response:** `200 OK` with paginated results:
  ```json
  {
    "count": 50,
    "next": "http://api.example.com/api/notes/?page=2",
    "previous": null,
    "results": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "My Note",
        "content_preview": "This is the first 200 characters of the note content...",
        "category": {
          "id": 1,
          "name": "Work",
          "color": "#10b981"
        },
        "updated_at": "2024-01-01T12:00:00Z"
      }
    ]
  }
  ```
* **Error Responses:**
  - `400 Bad Request`: Invalid category_id (doesn't belong to user)
  - `401 Unauthorized`: Missing or invalid access token
  - `429 Too Many Requests`: Rate limit exceeded

#### `GET /api/notes/{uuid}/` (Get Note)

* **Permission:** Authenticated (requires valid JWT)
* **Service Layer:** `note_service.get_note(user, note_uuid)`
* **Business Logic:**
  1. Query note by UUID and user_id
  2. Use `.select_related('category')` to avoid N+1 query
  3. Return 404 if note doesn't exist or belongs to another user (prevents ID enumeration)
* **Response:** `200 OK` with full note data:
  ```json
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "My Note",
    "content": "Full note content here...",
    "category": {
      "id": 1,
      "name": "Work",
      "color": "#10b981"
    },
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
  ```
* **Error Responses:**
  - `404 Not Found`: Note doesn't exist or belongs to another user
  - `401 Unauthorized`: Missing or invalid access token
  - `429 Too Many Requests`: Rate limit exceeded

#### `PATCH /api/notes/{uuid}/` (Update Note - Auto-save Implementation)

* **Permission:** Authenticated (requires valid JWT)
* **Input Validation:**
  - `title`: Optional string, max 255 characters
  - `content`: Optional string, max 100,000 characters
  - `category_id`: Optional integer, must belong to user
* **Service Layer:** `note_service.update_note(user, note_uuid, data)`
* **Business Logic:**
  1. Query note by UUID and user_id (raises `NotFound` if not found)
  2. Validate `category_id` belongs to user (if provided)
  3. Track old category_id before update
  4. Update only provided fields (partial update via `partial=True`)
  5. Automatically update `updated_at` timestamp (Django's `auto_now=True`)
  6. If category changed:
     a. Decrement old category note count in Redis cache
     b. Increment new category note count in Redis cache
  7. Transaction-wrapped to ensure atomicity
* **Response:** `200 OK` with updated note data (same format as GET)
* **Error Responses:**
  - `400 Bad Request`: Invalid category_id, title/content too long
  - `404 Not Found`: Note doesn't exist or belongs to another user
  - `401 Unauthorized`: Missing or invalid access token
  - `429 Too Many Requests`: Rate limit exceeded

#### `DELETE /api/notes/{uuid}/` (Delete Note)

* **Permission:** Authenticated (requires valid JWT)
* **Service Layer:** `note_service.delete_note(user, note_uuid)`
* **Business Logic:**
  1. Query note by UUID and user_id (raises `NotFound` if not found)
  2. Get category_id before deletion
  3. Delete note from database
  4. Decrement category note count in Redis cache (if category exists)
  5. Decrement user's total note count in cache (if applicable)
* **Response:** `204 No Content` (empty body)
* **Error Responses:**
  - `404 Not Found`: Note doesn't exist or belongs to another user
  - `401 Unauthorized`: Missing or invalid access token
  - `429 Too Many Requests`: Rate limit exceeded

## 4. Service Layer Implementation

### 4.1 Category Service (`category_service`)

The category service handles all business logic for category operations.

**Methods:**
- `list_categories(user)`: Returns all categories for user with note counts
- `create_category(user, data)`: Creates new category with validation
- `get_category(user, category_id)`: Retrieves single category with ownership check
- `update_category(user, category_id, data)`: Updates category with partial update
- `delete_category(user, category_id)`: Deletes category and updates notes

**Key Implementation Details:**
- All queries are scoped by `user_id` for multi-tenant isolation
- Category note counts are cached in Redis (key: `category:{category_id}:note_count`)
- "Random Thoughts" category is protected from deletion
- **Category name uniqueness is enforced per user scope** - the composite unique constraint on `(user_id, name)` ensures that within a user's categories, names must be unique, but different users can have categories with identical names

### 4.2 Note Service (`note_service`)

The note service handles all business logic for note operations.

**Methods:**
- `create_note(user, data)`: Creates new note with default category logic
- `list_notes(user, filters)`: Lists notes with filtering and pagination
- `get_note(user, note_uuid)`: Retrieves single note with ownership check
- `update_note(user, note_uuid, data)`: Updates note with category change handling
- `delete_note(user, note_uuid)`: Deletes note and updates category counts

**Key Implementation Details:**
- All queries are scoped by `user_id` for multi-tenant isolation
- Default category resolution: "Random Thoughts" → most recent category → NULL
- Category note counts are updated in Redis cache on create/update/delete
- Content preview is generated using SQL `LEFT(content, 200)` for efficiency
- Search uses case-insensitive `icontains` on both title and content

## 5. Serializers

### 5.1 Category Serializers

**CategorySerializer** (for create/update):
- `name`: CharField(max_length=100, required=True)
- `color`: CharField(max_length=7, required=False, default="#6366f1")
- Validation: name uniqueness per user, color hex format validation

**CategoryListSerializer** (for list responses):
- Includes all fields plus `note_count` from cache
- Read-only fields: id, created_at, updated_at, note_count

**CategoryDetailSerializer** (for detail responses):
- Same as CategoryListSerializer but includes full category data

### 5.2 Note Serializers

**NoteCreateSerializer** (for create):
- `title`: CharField(max_length=255, required=False, allow_blank=True)
- `content`: CharField(max_length=100000, required=False, allow_blank=True)
- `category_id`: IntegerField(required=False)
- Validation: category_id belongs to user

**NoteUpdateSerializer** (for update):
- Same fields as NoteCreateSerializer but all optional (partial=True)

**NoteListSerializer** (for list responses):
- `id`: UUIDField(read_only=True)
- `title`: CharField(read_only=True)
- `content_preview`: CharField(read_only=True) - generated via `LEFT(content, 200)` in SQL
- `category`: CategoryListSerializer(read_only=True) - nested serializer
- `updated_at`: DateTimeField(read_only=True)
- Excludes: `content` (full content), `created_at`

**NoteDetailSerializer** (for detail responses):
- `id`: UUIDField(read_only=True)
- `title`: CharField(read_only=True)
- `content`: CharField(read_only=True) - full content
- `category`: CategoryListSerializer(read_only=True) - nested serializer
- `created_at`: DateTimeField(read_only=True)
- `updated_at`: DateTimeField(read_only=True)

## 6. Security & Business Rules

### 6.1 Multi-Tenant Isolation

The backend implements a strict **Tenant Isolation Layer**. Every database query is scoped by `user_id`.

**Implementation Pattern:**
```python
# All querysets must filter by user
queryset = Note.objects.filter(user=request.user)
queryset = Category.objects.filter(user=request.user)
```

**Security Rule:** A `GET` request for a Note UUID or Category ID belonging to another user must return a `404 Not Found`, not a `403 Forbidden`. This prevents "ID Harvesting" (detecting if a specific ID exists in the system).

### 6.2 Resource Limits

To prevent database bloat and Denial of Service (DoS) via large payloads:

* **Title Limit:** 255 characters (enforced at database and serializer level)
* **Content Limit:** 100,000 characters (approx. 100KB per note, enforced at database and serializer level)
* **Category Name Limit:** 100 characters
* **Rate Limiting:** Authenticated users are subject to the general rate limit of 100 requests per hour per user (configurable via `RATE_LIMIT_USER_HOUR`). For high-frequency auto-saving scenarios, consider implementing endpoint-specific throttling or adjusting the global rate limit. The rate limiting uses Redis for distributed enforcement across multiple server instances.

### 6.3 Category Protection

* **"Random Thoughts" Protection:** The default "Random Thoughts" category cannot be deleted. Attempts to delete it return `400 Bad Request`.
* **Category Uniqueness:** Category names must be unique **within each user's scope** (enforced via composite unique constraint `(user_id, name)` and serializer validation). Different users can have categories with the same name without conflicts.

### 6.4 Data Integrity

* **Cascade Behavior:** 
  - User deletion: Cascades to delete all notes and categories (ON DELETE CASCADE)
  - Category deletion: Sets notes' `category_id` to NULL (ON DELETE SET NULL) to prevent data loss
* **Transaction Safety:** All multi-step operations (e.g., category deletion with note updates) are wrapped in database transactions to ensure atomicity.

## 7. Caching Strategy

### 7.1 Category Note Counts

Category note counts are cached in Redis to avoid expensive COUNT queries:

* **Cache Key Format:** `category:{category_id}:note_count`
* **Cache Value:** Integer count of notes in category
* **Cache Invalidation:**
  - Increment on note creation (if category provided)
  - Increment on note update (if category changed to this category)
  - Decrement on note update (if category changed from this category)
  - Decrement on note deletion (if category exists)
  - Reset to 0 on category creation
  - Remove on category deletion

**Cache Update Pattern:**
```python
# On note creation
if category_id:
    cache_key = f"category:{category_id}:note_count"
    cache.incr(cache_key, 1)  # Increment or initialize to 1

# On note deletion
if old_category_id:
    cache_key = f"category:{old_category_id}:note_count"
    cache.decr(cache_key, 1)  # Decrement (won't go below 0)
```

**Cache Fallback:** If cache miss, query database and repopulate cache:
```python
note_count = cache.get(cache_key)
if note_count is None:
    note_count = Note.objects.filter(category_id=category_id, user_id=user_id).count()
    cache.set(cache_key, note_count, timeout=3600)  # 1 hour TTL
```

### 7.2 Cache TTL

* **Category Note Counts:** 1 hour TTL (refreshed on mutations)
* **Purpose:** Balance between freshness and performance

## 8. Logic Flows

### 8.1 Note Creation Flow

```
1. Client sends POST /api/notes/ with {title?, content?, category_id?}
2. Authentication: Verify JWT using BlacklistCheckingJWTAuthentication
3. Serializer validates input (title <= 255, content <= 100000, category_id valid)
4. Service layer (create_note):
   a. If category_id omitted:
      i. Query user's "Random Thoughts" category
      ii. If not found, query most recent category for user
      iii. If no categories exist, use category_id = NULL
   b. If category_id provided: validate it belongs to user
   c. Create note with UUID primary key
   d. Increment category note count in Redis cache
5. Response: 201 Created with note data (including category info)
```

### 8.2 Note Update Flow (Auto-save)

```
1. Client sends PATCH /api/notes/{uuid}/ with {title?, content?, category_id?}
2. Authentication: Verify JWT using BlacklistCheckingJWTAuthentication
3. Serializer validates input (partial=True allows optional fields)
4. Service layer (update_note):
   a. Query note by UUID and user_id (404 if not found)
   b. Store old_category_id before update
   c. Validate new category_id belongs to user (if provided)
   d. Update note fields (only provided fields)
   e. Django automatically updates updated_at timestamp
   f. If category changed:
      i. Decrement old category note count in Redis
      ii. Increment new category note count in Redis
   g. All operations wrapped in database transaction
5. Response: 200 OK with updated note data
```

### 8.3 Category Deletion Flow

```
1. Client sends DELETE /api/categories/{id}/
2. Authentication: Verify JWT using BlacklistCheckingJWTAuthentication
3. Service layer (delete_category):
   a. Query category by ID and user_id (404 if not found)
   b. Check if category name is "Random Thoughts" (400 if yes)
   c. Begin database transaction:
      i. Update all notes with this category_id: SET category_id = NULL
      ii. Delete category from database
   d. Remove category note count from Redis cache
   e. Commit transaction
4. Response: 204 No Content
```

### 8.4 Note List with Search Flow

```
1. Client sends GET /api/notes/?search=keyword&category_id=1&page=1
2. Authentication: Verify JWT using BlacklistCheckingJWTAuthentication
3. Service layer (list_notes):
   a. Start with queryset: Note.objects.filter(user=user)
   b. If category_id provided: validate belongs to user, then filter
   c. If search provided: apply Q(title__icontains=search) | Q(content__icontains=search)
   d. Order by -updated_at
   e. Use .select_related('category') to avoid N+1 queries
   f. Apply pagination (PageNumberPagination, page_size=20)
   g. Use NoteListSerializer (includes content_preview, excludes full content)
4. Response: 200 OK with paginated results
```

## 9. Error Handling

### 9.1 Error Response Format

All errors follow DRF's standard error format:

```json
{
  "detail": "Error message here",
  "code": "error_code"  // Optional
}
```

### 9.2 Common Error Scenarios

| Status Code | Scenario | Error Message |
| --- | --- | --- |
| `400 Bad Request` | Invalid input, duplicate category name, deleting "Random Thoughts", invalid category_id | Validation error details |
| `404 Not Found` | Note/Category doesn't exist or belongs to another user | "Not found." |
| `401 Unauthorized` | Missing or invalid JWT token | "Authentication credentials were not provided." or "Token has been revoked" |
| `429 Too Many Requests` | Rate limit exceeded | Standard DRF throttle error |

### 9.3 Validation Error Details

**Category Name Uniqueness:**
```json
{
  "name": ["A category with this name already exists."]
}
```

**Category Deletion Protection:**
```json
{
  "detail": "Cannot delete the 'Random Thoughts' category."
}
```

**Invalid Category Reference:**
```json
{
  "category_id": ["Category does not exist or does not belong to you."]
}
```