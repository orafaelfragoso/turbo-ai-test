# NoteApp Backend

Django REST Framework microservice API with OAuth2-compliant JWT authentication.

## 🏗️ Architecture

This backend follows microservice architecture principles:

- **Framework**: Django REST Framework 3.14+
- **Database**: PostgreSQL 16 with JSONB support
- **Cache/Broker**: Redis for JWT blacklisting, rate limiting, and Celery task queue
- **Task Queue**: Celery for background job processing
- **Authentication**: JWT with access/refresh token pattern and Redis-backed blacklist
- **Rate Limiting**: Per-user throttling with Redis backend (100 req/hour)
- **API Versioning**: Accept header versioning (v1)
- **Documentation**: OpenAPI 3.0 with Swagger UI and ReDoc
- **Deployment**: Gunicorn WSGI server with multiple workers

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
│   └── auth/                   # Authentication application
│       ├── models.py           # User model
│       ├── serializers.py      # Request/response validation
│       ├── views.py            # API endpoints (thin controllers)
│       ├── services.py         # Business logic layer
│       ├── tasks.py            # Celery background tasks
│       ├── urls.py             # App URL routing
│       ├── admin.py            # Django admin configuration
│       ├── throttles.py        # Rate limiting classes
│       ├── authentication.py   # Custom JWT auth with blacklist
│       └── tests/              # Comprehensive test suite
│           ├── test_models.py
│           ├── test_serializers.py
│           ├── test_services.py
│           ├── test_tasks.py
│           ├── test_views.py
│           ├── test_throttles.py
│           ├── test_versioning.py
│           └── test_logout.py
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

## 🚦 Rate Limiting

The API implements per-user rate limiting using Redis to prevent abuse:

### Configuration

- **Authenticated Users**: 100 requests per hour per user (configurable)
- **Anonymous Users**: 20 requests per hour per IP (configurable)
- **Backend**: Redis cache for distributed rate limiting
- **Response**: HTTP 429 (Too Many Requests) when limit exceeded

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
```

### Test Structure

```
apps/auth/tests/
├── test_models.py          # User model tests
├── test_serializers.py     # Validation and transformation tests
├── test_services.py        # Business logic tests (80%+ coverage)
├── test_tasks.py           # Celery task tests
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

## 🏛️ Architecture Patterns

### Service Layer Pattern

**Purpose**: Separate business logic from views for better testability and reusability.

**Structure**:
```python
# views.py - Thin controllers
class SignupView(APIView):
    """Handle HTTP request/response only"""
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Delegate to service
        user_data = auth_service.register_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )
        
        return Response(user_data, status=201)

# services.py - Business logic
class AuthService:
    """Encapsulate business logic and transactions"""
    @staticmethod
    @transaction.atomic
    def register_user(email: str, password: str) -> Dict:
        # Validation
        if User.objects.filter(email=email).exists():
            raise ValidationError({'email': 'Email already exists'})
        
        # Business logic
        user = User.objects.create_user(email=email, password=password)
        
        # Trigger side effects
        initialize_user_environment.delay(user.id)
        
        return {'id': user.id, 'email': user.email, 'created_at': user.created_at}
```

**Benefits**:
- Views remain thin and focused on HTTP
- Services are testable independently
- Business logic is reusable
- Transactions handled properly
- Clear separation of concerns

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

## 📈 Performance

### Database
- Connection pooling via `CONN_MAX_AGE`
- Index on `email` field (unique constraint)
- Database-level constraints for data integrity

### Caching
- Redis for JWT denylist (fast lookups)
- Future: Cache expensive queries

### Scalability
- Stateless API design
- Horizontal scaling via Gunicorn workers
- Celery workers for background tasks
- Database read replicas (future)

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
