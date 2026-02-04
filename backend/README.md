# Notes app backend

Django REST Framework microservice API for the notes application.

## 🏗️ Architecture

This backend follows microservice architecture principles with a service layer pattern:

- **Framework**: Django REST Framework 3.14+
- **Database**: PostgreSQL 16 with JSONB support and UUID primary keys
- **Cache/Broker**: Redis for JWT blacklisting, rate limiting, category note counts, and Celery task queue
- **Task Queue**: Celery for background job processing
- **Authentication**: JWT with access/refresh token pattern and Redis-backed blacklist
- **Rate Limiting**: Per-user throttling with Redis backend (100 req/hour)
- **API Versioning**: Accept header versioning (v1)
- **Documentation**: OpenAPI 3.0 with Swagger UI and ReDoc
- **Deployment**: Gunicorn WSGI server with multiple workers
- **Multi-Tenancy**: User-scoped data isolation for notes and categories

## 📁 Project Structure

```
backend/
├── api/                        # Django project configuration
│   ├── settings/               # Split settings pattern
│   │   ├── base.py             # Shared settings
│   │   ├── development.py      # Development overrides
│   │   └── production.py       # Production overrides
│   ├── celery.py               # Celery configuration
│   ├── urls.py                 # Root URL configuration
│   ├── wsgi.py                 # WSGI entry point
│   └── asgi.py                 # ASGI entry point (future)
├── apps/                       # Django applications
│   ├── auth/                   # Authentication application
│   │   ├── models.py           # User model
│   │   ├── serializers.py      # Request/response validation
│   │   ├── views.py            # API endpoints (thin controllers)
│   │   ├── services.py         # Business logic layer
│   │   ├── tasks.py            # Celery background tasks
│   │   ├── urls.py             # App URL routing
│   │   ├── admin.py            # Django admin configuration
│   │   ├── throttles.py        # Rate limiting classes
│   │   ├── authentication.py   # Custom JWT auth with blacklist
│   │   └── tests/              # Comprehensive test suite
│   │       ├── test_models.py
│   │       ├── test_serializers.py
│   │       ├── test_services.py
│   │       ├── test_tasks.py
│   │       ├── test_views.py
│   │       ├── test_throttles.py
│   │       ├── test_versioning.py
│   │       └── test_logout.py
│   └── notes/                  # Notes and categories application
│       ├── models.py           # Note and Category models
│       ├── serializers.py      # Request/response validation
│       ├── views.py            # API endpoints (ViewSets)
│       ├── services.py         # Business logic layer
│       ├── urls.py             # App URL routing
│       ├── admin.py            # Django admin configuration
│       └── tests/              # Comprehensive test suite
│           ├── test_models.py
│           ├── test_serializers.py
│           ├── test_services.py
│           └── test_views.py
├── conftest.py                 # Pytest fixtures
├── pytest.ini                  # Pytest configuration
├── pyproject.toml              # Poetry dependencies and tool config
├── Dockerfile                  # Multi-stage production build
└── docker-entrypoint.sh        # Container startup script
```

## 🚀 Setup

### Local Development with Poetry

1. **Install dependencies**:
   ```bash
   cd backend
   poetry install
   ```

2. **Activate virtual environment**:
   ```bash
   poetry env activate
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**:
   ```bash
   python manage.py runserver
   ```

7. **Run Celery worker** (in separate terminal):
   ```bash
   celery -A api worker --loglevel=info
   ```

### Docker Development

See root `README.md` for Docker Compose instructions.

## 🔐 Authentication API

### Overview

The backend provides OAuth2-compliant JWT authentication with:
- Short-lived access tokens (15 minutes)
- Long-lived refresh tokens (7 days)
- Token revocation via Redis denylist
- Secure password hashing (PBKDF2)

### Endpoints

#### 1. User Registration

```http
POST /api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (201 Created)**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2024-01-01T12:00:00Z"
}
```

**Notes**:
- Triggers background task `initialize_user_environment` for async setup
- Email must be unique
- Password must meet security requirements

**Errors**:
- `400 Bad Request`: Invalid email or password format
- `400 Bad Request`: Email already exists

#### 2. User Sign-In

```http
POST /api/auth/signin
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer"
}
```

**Token Details**:
- `access_token`: Use for authenticated requests (expires in 15 minutes)
- `refresh_token`: Use to obtain new access tokens (expires in 7 days)
- `token_type`: Always "Bearer"

**Errors**:
- `401 Unauthorized`: Invalid credentials

#### 3. Token Refresh

```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer"
}
```

**Notes**:
- Validates refresh token and issues new access token
- Refresh token remains valid (not rotated)

**Errors**:
- `401 Unauthorized`: Invalid or expired refresh token
- `401 Unauthorized`: Token in denylist (user logged out)

#### 4. User Logout

```http
POST /api/auth/logout
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK)**:
```json
{
  "message": "Successfully logged out"
}
```

**Notes**:
- Requires authentication (access token in Authorization header)
- Blacklists refresh token in Redis to prevent reuse
- Token cannot be used after logout

**Errors**:
- `401 Unauthorized`: Missing or invalid access token
- `401 Unauthorized`: Invalid refresh token
- `429 Too Many Requests`: Rate limit exceeded

#### 5. Health Check

```http
GET /api/health/
```

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Using JWT Tokens

Include the access token in the Authorization header for protected endpoints:

```http
GET /api/protected-endpoint
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Token Lifecycle

1. **Registration**: User signs up → receives user data
2. **Sign-In**: User authenticates → receives access + refresh tokens
3. **Access**: User makes requests with access token
4. **Refresh**: Access token expires → use refresh token to get new access token
5. **Logout**: User logs out → refresh token blacklisted in Redis (cannot be reused)

## 📝 Notes & Categories API

### Overview

The backend provides a complete note-taking system with:
- User-scoped categories for organizing notes
- Full CRUD operations on notes and categories
- UUID primary keys for security (prevents ID enumeration)
- Redis-backed caching for category note counts
- Pagination, filtering, and search capabilities
- Auto-save pattern with partial updates

**Authentication**: All endpoints require a valid JWT access token in the `Authorization: Bearer` header.

**Multi-Tenant Isolation**: All data is strictly isolated per user. Users can only access their own notes and categories.

### Category Endpoints

#### 1. List Categories

```http
GET /api/categories/
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
[
  {
    "id": 1,
    "name": "Random Thoughts",
    "color": "#6366F1",
    "note_count": 5,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  },
  {
    "id": 2,
    "name": "Work",
    "color": "#10B981",
    "note_count": 12,
    "created_at": "2024-01-02T12:00:00Z",
    "updated_at": "2024-01-02T12:00:00Z"
  }
]
```

**Notes**:
- Returns all categories for the authenticated user
- Includes cached note count for each category
- Ordered by creation date (oldest first)

**Errors**:
- `401 Unauthorized`: Missing or invalid access token
- `429 Too Many Requests`: Rate limit exceeded

#### 2. Create Category

```http
POST /api/categories/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Personal",
  "color": "#EF4444"
}
```

**Response (201 Created)**:
```json
{
  "id": 3,
  "name": "Personal",
  "color": "#EF4444",
  "note_count": 0,
  "created_at": "2024-01-03T12:00:00Z",
  "updated_at": "2024-01-03T12:00:00Z"
}
```

**Notes**:
- `name`: Required, 1-100 characters, must be unique per user
- `color`: Optional, valid hex color code (default: `#6366f1`)
- Category names are unique within each user's scope, not globally

**Errors**:
- `400 Bad Request`: Invalid name or color format
- `400 Bad Request`: Category name already exists for this user
- `401 Unauthorized`: Missing or invalid access token
- `429 Too Many Requests`: Rate limit exceeded

#### 3. Get Category

```http
GET /api/categories/{id}/
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
{
  "id": 1,
  "name": "Random Thoughts",
  "color": "#6366F1",
  "note_count": 5,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Errors**:
- `404 Not Found`: Category doesn't exist or belongs to another user
- `401 Unauthorized`: Missing or invalid access token
- `429 Too Many Requests`: Rate limit exceeded

#### 4. Update Category

```http
PATCH /api/categories/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Work Projects",
  "color": "#8B5CF6"
}
```

**Response (200 OK)**:
```json
{
  "id": 2,
  "name": "Work Projects",
  "color": "#8B5CF6",
  "note_count": 12,
  "created_at": "2024-01-02T12:00:00Z",
  "updated_at": "2024-01-03T14:30:00Z"
}
```

**Notes**:
- Partial update supported (provide only fields to update)
- `name` must be unique per user if provided
- `color` must be valid hex format if provided

**Errors**:
- `400 Bad Request`: Invalid name or color, duplicate category name
- `404 Not Found`: Category doesn't exist or belongs to another user
- `401 Unauthorized`: Missing or invalid access token
- `429 Too Many Requests`: Rate limit exceeded

#### 5. Delete Category

```http
DELETE /api/categories/{id}/
Authorization: Bearer {access_token}
```

**Response (204 No Content)**

**Notes**:
- Cannot delete "Random Thoughts" category (protected default)
- All notes in this category will have their category set to `null`
- Deletion is transaction-wrapped for data integrity

**Errors**:
- `400 Bad Request`: Attempting to delete "Random Thoughts" category
- `404 Not Found`: Category doesn't exist or belongs to another user
- `401 Unauthorized`: Missing or invalid access token
- `429 Too Many Requests`: Rate limit exceeded

### Note Endpoints

#### 1. List Notes

```http
GET /api/notes/?category_id=1&search=keyword&page=1&page_size=20
Authorization: Bearer {access_token}
```

**Query Parameters**:
- `category_id` (optional): Filter by category ID
- `search` (optional): Search in title and content (case-insensitive)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)

**Response (200 OK)**:
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
        "color": "#10B981"
      },
      "updated_at": "2024-01-03T15:30:00Z"
    }
  ]
}
```

**Notes**:
- Returns paginated list of notes for authenticated user
- `content_preview` shows first 200 characters
- Ordered by most recently updated first
- Search filters on both title and content

**Errors**:
- `400 Bad Request`: Invalid category_id (doesn't belong to user)
- `401 Unauthorized`: Missing or invalid access token
- `429 Too Many Requests`: Rate limit exceeded

#### 2. Create Note

```http
POST /api/notes/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Meeting Notes",
  "content": "Discussed project timeline and deliverables",
  "category_id": 2
}
```

**Response (201 Created)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Meeting Notes",
  "content": "Discussed project timeline and deliverables",
  "category": {
    "id": 2,
    "name": "Work",
    "color": "#10B981"
  },
  "created_at": "2024-01-03T16:00:00Z",
  "updated_at": "2024-01-03T16:00:00Z"
}
```

**Notes**:
- All fields are optional
- If `category_id` is omitted, defaults to "Random Thoughts" category
- If "Random Thoughts" doesn't exist, uses most recent category
- `title` max 255 characters
- `content` max 100,000 characters

**Errors**:
- `400 Bad Request`: Invalid category_id, title/content too long
- `401 Unauthorized`: Missing or invalid access token
- `429 Too Many Requests`: Rate limit exceeded

#### 3. Get Note

```http
GET /api/notes/{uuid}/
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Meeting Notes",
  "content": "Discussed project timeline and deliverables",
  "category": {
    "id": 2,
    "name": "Work",
    "color": "#10B981"
  },
  "created_at": "2024-01-03T16:00:00Z",
  "updated_at": "2024-01-03T16:00:00Z"
}
```

**Notes**:
- Returns full note content (not preview)
- UUID prevents ID enumeration attacks

**Errors**:
- `404 Not Found`: Note doesn't exist or belongs to another user
- `401 Unauthorized`: Missing or invalid access token
- `429 Too Many Requests`: Rate limit exceeded

#### 4. Update Note (Auto-save)

```http
PATCH /api/notes/{uuid}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Updated Meeting Notes",
  "content": "Discussed project timeline, deliverables, and budget",
  "category_id": 3
}
```

**Response (200 OK)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Updated Meeting Notes",
  "content": "Discussed project timeline, deliverables, and budget",
  "category": {
    "id": 3,
    "name": "Personal",
    "color": "#EF4444"
  },
  "created_at": "2024-01-03T16:00:00Z",
  "updated_at": "2024-01-03T16:30:00Z"
}
```

**Notes**:
- Partial update supported (provide only fields to update)
- `updated_at` automatically refreshed
- Category change updates cached note counts
- Ideal for auto-save implementations

**Errors**:
- `400 Bad Request`: Invalid category_id, title/content too long
- `404 Not Found`: Note doesn't exist or belongs to another user
- `401 Unauthorized`: Missing or invalid access token
- `429 Too Many Requests`: Rate limit exceeded

#### 5. Delete Note

```http
DELETE /api/notes/{uuid}/
Authorization: Bearer {access_token}
```

**Response (204 No Content)**

**Notes**:
- Permanently deletes the note
- Updates cached category note count

**Errors**:
- `404 Not Found`: Note doesn't exist or belongs to another user
- `401 Unauthorized`: Missing or invalid access token
- `429 Too Many Requests`: Rate limit exceeded

### Data Models

#### Category Model

Categories organize notes and are scoped per user:

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer (PK) | Auto-incrementing primary key |
| `user_id` | Foreign Key | Reference to user (CASCADE on delete) |
| `name` | String (100) | Category name, unique per user |
| `color` | String (7) | Hex color code (e.g., `#6366f1`) |
| `created_at` | Timestamp | Auto-created timestamp |
| `updated_at` | Timestamp | Auto-updated timestamp |

**Key Features**:
- **User-Scoped Uniqueness**: Composite unique constraint on `(user_id, name)` ensures category names are unique within each user's scope, not globally. Multiple users can have categories with the same name.
- **Default Category**: "Random Thoughts" category is automatically created during user initialization
- **Protected Deletion**: "Random Thoughts" category cannot be deleted
- **Cascade Behavior**: Deleting a user cascades to delete all their categories
- **Note Relationship**: Deleting a category sets notes' `category_id` to `NULL` (preserves notes)

**Database Indexes**:
- Primary key on `id`
- Index on `user_id` for user-scoped queries
- Composite index on `(user_id, name)` for uniqueness and lookups

#### Note Model

Notes are the core content entities with UUID primary keys for security:

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID (PK) | UUID v4 primary key (prevents enumeration) |
| `user_id` | Foreign Key | Reference to user (CASCADE on delete) |
| `category_id` | Foreign Key (nullable) | Reference to category (SET NULL on delete) |
| `title` | String (255) | Note title (optional) |
| `content` | Text | Note content, max 100,000 characters |
| `created_at` | Timestamp | Auto-created timestamp |
| `updated_at` | Timestamp | Auto-updated timestamp (for sorting) |

**Key Features**:
- **UUID Primary Keys**: Prevents ID enumeration attacks - users cannot guess other users' note IDs
- **Optional Category**: Notes can exist without a category
- **Auto-save Ready**: `updated_at` automatically updates on every save
- **Large Content Support**: PostgreSQL TOAST handles large text efficiently
- **Multi-Tenant Isolation**: All queries strictly scoped by `user_id`

**Database Indexes**:
- Primary key on `id` (UUID)
- Index on `user_id` for user-scoped queries
- Index on `category_id` for category filtering
- Composite index on `(user_id, updated_at)` for efficient "recent notes" queries
- Index on `title` for prefix searches
- Index on `updated_at` for sorting

**Constraints**:
- Title max length: 255 characters
- Content max length: 100,000 characters
- Foreign key to categories with SET NULL on delete
- Foreign key to users with CASCADE on delete

## 🚦 Rate Limiting

The API implements per-user rate limiting using Redis to prevent abuse:

### Configuration

- **Authenticated Users**: 100 requests per hour per user (configurable)
- **Anonymous Users**: 20 requests per hour per IP (configurable)
- **Backend**: Redis cache for distributed rate limiting
- **Response**: HTTP 429 (Too Many Requests) when limit exceeded
- **Applies To**: All API endpoints including authentication, notes, and categories

### Rate Limit Headers

When rate limited, the response includes:
```json
{
  "detail": "Request was throttled. Expected available in X seconds."
}
```

### Configuring Rate Limits

Set environment variables in `.env`:
```bash
RATE_LIMIT_USER_HOUR=100    # Requests per hour for authenticated users
RATE_LIMIT_ANON_HOUR=20     # Requests per hour for anonymous users
```

## 🔄 API Versioning

The API uses **Accept header versioning** following REST best practices:

### Request Format

Include the version in the Accept header:
```http
GET /api/auth/signin
Accept: application/vnd.noteapp.v1+json
```

### Default Behavior

- If no version header is provided, defaults to `v1`
- Standard `application/json` Accept header also works

### Current Version

- **v1**: Current stable version

### Example

```bash
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Accept: application/vnd.noteapp.v1+json" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

## 📚 API Documentation

Interactive API documentation is automatically generated using OpenAPI 3.0 (Swagger):

### Documentation URLs

- **Swagger UI**: http://localhost:8000/api/docs/
  - Interactive API explorer
  - Try endpoints directly from browser
  - Authentication supported
  
- **ReDoc**: http://localhost:8000/api/redoc/
  - Clean, readable documentation
  - Better for reading than testing

- **OpenAPI Schema**: http://localhost:8000/api/schema/
  - JSON schema for API clients
  - Use with code generators

### Features

- Complete endpoint documentation with examples
- Request/response schemas
- Authentication flows
- Error responses
- Try-it-out functionality

### Using Swagger UI

1. Open http://localhost:8000/api/docs/
2. Click "Authorize" button
3. Enter your JWT access token (without "Bearer" prefix)
4. Test endpoints directly from the browser

## 🧪 Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=apps --cov-report=html

# Run specific test file
poetry run pytest apps/auth/tests/test_services.py

# Run with verbose output
poetry run pytest -v

# Run specific test
poetry run pytest apps/auth/tests/test_views.py::TestSignupView::test_signup_success

# Run notes tests
poetry run pytest apps/notes/tests/

# Run specific notes test
poetry run pytest apps/notes/tests/test_services.py::TestNoteService::test_create_note
```

### Test Structure

```
apps/auth/tests/
├── test_models.py          # User model tests
├── test_serializers.py     # Validation and transformation tests
├── test_services.py        # Business logic tests (80%+ coverage)
├── test_tasks.py           # Celery task tests
├── test_views.py           # API integration tests
├── test_throttles.py       # Rate limiting tests
├── test_versioning.py      # API versioning tests
└── test_logout.py          # Logout flow tests

apps/notes/tests/
├── test_models.py          # Note and Category model tests
├── test_serializers.py     # Validation and transformation tests
├── test_services.py        # Business logic tests (80%+ coverage)
└── test_views.py           # API integration tests
```

### Test Fixtures

Centralized fixtures in `conftest.py`:
- `db`: Database access
- `user`: Test user instance
- `api_client`: Django REST Framework test client
- Custom fixtures as needed

### Coverage Requirements

- **Services**: 80%+ coverage (business logic critical)
- **Views**: High coverage (API contracts)
- **Serializers**: Validation coverage
- **Models**: Basic coverage

View coverage report:
```bash
poetry run pytest --cov=apps --cov-report=html
open htmlcov/index.html
```

## 🎨 Code Quality

### Formatting with Black

```bash
# Format all code
poetry run black .

# Check formatting without changes
poetry run black --check .

# Format specific file
poetry run black apps/auth/services.py
```

**Configuration** (`pyproject.toml`):
- Line length: 88 characters
- Target: Python 3.12
- Exclude: migrations, venv, __pycache__

### Linting with Ruff

```bash
# Lint all code
poetry run ruff check .

# Fix auto-fixable issues
poetry run ruff check --fix .

# Lint specific file
poetry run ruff check apps/auth/services.py
```

**Configuration** (`pyproject.toml`):
- PEP 8 enforcement
- Import sorting
- Logic error detection
- Unused variable detection

### Type Checking (Optional)

```bash
# Type check with mypy
poetry run mypy apps/
```

## 🌍 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key (50+ chars) | `your-secret-key-here` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/db` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://localhost:6379/1` |
| `GUNICORN_WORKERS` | Gunicorn worker processes | `4` |
| `GUNICORN_THREADS` | Threads per worker | `2` |
| `JWT_ACCESS_TOKEN_LIFETIME` | Access token lifetime (minutes) | `15` |
| `JWT_REFRESH_TOKEN_LIFETIME` | Refresh token lifetime (minutes) | `10080` (7 days) |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |
| `RATE_LIMIT_USER_HOUR` | Rate limit for authenticated users (per hour) | `100` |
| `RATE_LIMIT_ANON_HOUR` | Rate limit for anonymous users (per hour) | `20` |
| `API_VERSION_DEFAULT` | Default API version | `v1` |

## 🐳 Docker

### Building and Running

```bash
# Build image
docker build -t noteapp-backend .

# Run container
docker run -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=postgresql://... \
  noteapp-backend

# With Docker Compose (from root)
docker-compose up --build
```

### Docker Services

The `docker-compose.yml` defines:
- **postgres**: PostgreSQL 16 database
- **redis**: Redis 7 cache/broker
- **api**: Django backend (this service)
- **celery_worker**: Celery task processor

### Container Management

```bash
# View logs
docker-compose logs -f api

# Execute commands
docker-compose exec api python manage.py migrate
docker-compose exec api python manage.py createsuperuser
docker-compose exec api python manage.py shell

# Restart service
docker-compose restart api

# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION)
docker-compose down -v
```

## 📊 Database

### Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Rollback migration
python manage.py migrate auth 0001

# In Docker
docker-compose exec api python manage.py makemigrations
docker-compose exec api python manage.py migrate
```

### Database Shell

```bash
# PostgreSQL shell
docker-compose exec postgres psql -U noteapp_user -d noteapp_db

# Django shell
python manage.py shell

# Django dbshell
python manage.py dbshell
```

## 🔧 Celery

### Running Celery

```bash
# Worker
celery -A api worker --loglevel=info

# With autoreload for development
watchfiles --filter python 'celery -A api worker --loglevel=info'

# In Docker
docker-compose up celery_worker
```

### Monitoring Tasks

```bash
# Celery events
celery -A api events

# Flower (task monitoring UI)
celery -A api flower
```

### Available Tasks

- `initialize_user_environment(user_id)`: Initialize user environment after registration
  - Creates default "Random Thoughts" category for the user
  - Triggered automatically on user signup

## 🏛️ Architecture Patterns

### Service Layer Pattern

**Purpose**: Separate business logic from views for better testability and reusability.

**Structure**:
```python
# views.py - Thin controllers (ViewSets for notes)
class NoteViewSet(viewsets.ViewSet):
    """Handle HTTP request/response only"""
    authentication_classes = [BlacklistCheckingJWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    def create(self, request):
        serializer = NoteCreateSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        
        # Delegate to service
        note = note_service.create_note(request.user, serializer.validated_data)
        
        response_serializer = NoteDetailSerializer(note)
        return Response(response_serializer.data, status=201)

# services.py - Business logic
class NoteService:
    """Encapsulate business logic and transactions"""
    @staticmethod
    @transaction.atomic
    def create_note(user, data):
        """Create a new note with default category logic."""
        title = data.get('title', '')
        content = data.get('content', '')
        category_id = data.get('category_id')
        
        # Determine category (Random Thoughts → most recent → None)
        if category_id is not None:
            category = Category.objects.get(id=category_id, user=user)
        else:
            category = self._get_default_category(user)
        
        # Create note
        note = Note.objects.create(
            user=user, category=category, title=title, content=content
        )
        
        # Update cached category note count
        if category:
            cache_key = f"category:{category.id}:note_count"
            try:
                cache.incr(cache_key)
            except ValueError:
                # Cache miss - repopulate from database
                note_count = Note.objects.filter(category=category).count()
                cache.set(cache_key, note_count, timeout=3600)
        
        return note
```

**Benefits**:
- Views remain thin and focused on HTTP
- Services are testable independently
- Business logic is reusable
- Transactions handled properly
- Clear separation of concerns
- Multi-tenant isolation enforced at service layer

### Custom User Model

The project uses a custom user model with email as the username field:

```python
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
```

**Benefits**:
- Email-based authentication (modern UX)
- Extensible for future fields
- Follows Django best practices

## 🔒 Security

### Password Security
- **Hashing**: PBKDF2 with SHA256 (Django default)
- **Validation**: Django password validators
- **Salting**: Automatic per-user salt

### JWT Security
- **Short-lived access tokens**: 15-minute expiration
- **Token revocation**: Redis denylist for logout
- **Signature verification**: HMAC SHA256

### API Security
- **CORS**: Configured allowed origins
- **CSRF**: Disabled for API (token-based auth)
- **SQL Injection**: ORM parameterized queries
- **XSS**: JSON responses (no HTML rendering)

### Notes & Categories Security

#### Multi-Tenant Isolation
All database queries are strictly scoped by `user_id` to enforce data isolation:

```python
# All queries filter by authenticated user
notes = Note.objects.filter(user=request.user)
categories = Category.objects.filter(user=request.user)
```

**Security Rule**: When a user requests a resource that doesn't exist or belongs to another user, the API returns `404 Not Found` (not `403 Forbidden`). This prevents ID harvesting attacks where attackers could enumerate valid resource IDs.

#### UUID Primary Keys for Notes
Notes use UUID v4 primary keys instead of sequential integers:
- **Prevents ID enumeration**: Users cannot guess valid note IDs
- **Non-sequential**: No information leakage about total notes or creation order
- **Collision-resistant**: UUID v4 has negligible collision probability

#### Resource Limits
To prevent abuse and database bloat:
- **Note title**: Max 255 characters
- **Note content**: Max 100,000 characters (~100KB per note)
- **Category name**: Max 100 characters
- **Rate limiting**: 100 requests/hour per authenticated user

#### Category Protection
- **Default Category**: "Random Thoughts" category cannot be deleted
- **User-Scoped Uniqueness**: Category names are unique per user (not globally), enforced via composite constraint on `(user_id, name)`
- **Cascade Behavior**: 
  - Deleting a user cascades to delete all their notes and categories
  - Deleting a category sets notes' `category_id` to `NULL` (preserves notes)

## 📈 Performance

### Database
- Connection pooling via `CONN_MAX_AGE`
- Strategic indexes for query optimization:
  - `email` field (unique constraint)
  - `user_id` on notes and categories (tenant isolation)
  - Composite `(user_id, updated_at)` on notes (recent notes queries)
  - `(user_id, name)` on categories (uniqueness + lookups)
- Database-level constraints for data integrity
- `.select_related('category')` to prevent N+1 queries

### Caching Strategy

#### JWT Blacklist
- **Cache Key**: `blacklist:{jti}`
- **Purpose**: Fast lookup for revoked tokens
- **TTL**: Token expiration time

#### Category Note Counts
- **Cache Key**: `category:{category_id}:note_count`
- **Purpose**: Avoid expensive COUNT queries on category list
- **TTL**: 1 hour (3600 seconds)
- **Invalidation**:
  - Increment on note creation
  - Increment/decrement on note category change
  - Decrement on note deletion
  - Remove on category deletion
- **Fallback**: On cache miss, query database and repopulate cache

**Cache Update Example**:
```python
# On note creation
if category_id:
    cache_key = f"category:{category_id}:note_count"
    try:
        cache.incr(cache_key)  # Atomic increment
    except ValueError:
        # Cache miss - query DB and set
        note_count = Note.objects.filter(category_id=category_id).count()
        cache.set(cache_key, note_count, timeout=3600)
```

### Scalability
- Stateless API design
- Horizontal scaling via Gunicorn workers
- Redis-backed caching for distributed systems
- Celery workers for background tasks
- Database read replicas (future)
- Pagination for large result sets (max 100 items per page)

## 🔧 Development Workflow

### Creating a New App

```bash
# Create app
python manage.py startapp myapp apps/myapp

# Register in settings
# Add 'apps.myapp' to INSTALLED_APPS

# Create models, views, serializers, services
# Write tests
# Run tests
poetry run pytest apps/myapp/tests/
```

### Adding Dependencies

```bash
# Add dependency
poetry add package-name

# Add dev dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Export requirements.txt (if needed)
poetry export -f requirements.txt --output requirements.txt
```
