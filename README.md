# Notes App

A production-grade note-taking application built to demonstrate how a senior software engineer can architect and deliver enterprise-level solutions in days using AI assistance.

## Introduction

### How I Built This

I orchestrated AI tools to execute my architectural vision:

1. **Design Phase**: Used Gemini to generate multiple PRDs from demo video transcriptions, then defined the architectural patterns, technology stack, and end goals myself
2. **Implementation Phase**: Used Cursor/Claude to assist with configuration, development, and debugging while I validated every decision with my engineering expertise
3. **Role**: I was the architect; AI was the execution engine working under my direction

This project demonstrates how years of experience in building scalable systems translates into rapid, high-quality delivery when paired with AI assistance.

### Philosophy

Every architectural and technology decision was made with three priorities:
- **Scalability**: Horizontal scaling, stateless design, cloud-native patterns
- **Maintainability**: Service layer architecture, 80%+ test coverage, strict separation of concerns
- **Developer Experience**: Docker environments, Makefile automation, comprehensive documentation

### What I Built

- OAuth2-compliant JWT authentication with Redis blacklist
- Service Layer architecture pattern for clean business logic separation
- 80%+ test coverage with pytest
- All 12 factors of cloud-native application design
- Production-ready Docker containerization with multi-stage builds
- Background task processing with Celery
- Multi-tenant data isolation with security-first design

## Backend

### Architecture: Service Layer Pattern

I implemented the Service Layer pattern to separate business logic from HTTP request handling.

**Why**: Testability, reusability, and maintainability. Views become thin controllers, services encapsulate complex logic with transaction management.

**Impact**: 
- Business logic independently testable without HTTP mocking
- Transaction boundaries clearly defined
- Easy to reuse logic across different endpoints or background tasks

**Example**: [`backend/apps/auth/services.py`](backend/apps/auth/services.py) handles user registration, authentication, and token management while [`backend/apps/auth/views.py`](backend/apps/auth/views.py) only deals with HTTP concerns.

### Technology Stack

#### Django REST Framework + Python 3.12

**Why**: Mature ecosystem with batteries-included approach enables rapid development without sacrificing robustness. Built-in admin, ORM security, and extensive middleware ecosystem.

**Impact**: Reduced boilerplate, automatic SQL injection prevention, instant admin panel for operations.

#### PostgreSQL 16

**Why**: JSONB support for flexible schemas, robust ACID transactions, excellent performance at scale. UUID primary keys for notes prevent ID enumeration attacks.

**Impact**: Enhanced security (non-guessable IDs), better suited for distributed systems, powerful query capabilities.

#### Redis

**Why**: In-memory performance for three critical use cases:
1. JWT blacklist for instant token revocation checks
2. Rate limiting with distributed counter support
3. Category note counts cache (atomic increments, 1-hour TTL)

**Impact**: Sub-millisecond token validation, distributed rate limiting across API instances, 90%+ reduction in database queries for category listings.

#### Celery

**Why**: Offload long-running operations from request/response cycle.

**Example**: `initialize_user_environment` task runs asynchronously after signup to create default categories without blocking the HTTP response.

**Impact**: Faster API responses, better user experience, resilient async processing with retries.

### Security

#### JWT with Redis Blacklist

**Decision**: Hybrid approach combining stateless JWT benefits with logout capability via Redis blacklist.

**Implementation**: Custom `BlacklistCheckingJWTAuthentication` checks Redis before accepting tokens. Tokens blacklisted on logout remain invalid even if not expired.

**Trade-off**: Adds Redis dependency but enables proper logout—critical for production applications.

#### Multi-Tenant Isolation

**Strategy**: All database queries strictly scoped by `user_id`. Return 404 (not 403) for non-existent resources to prevent ID harvesting.

**Impact**: Complete data isolation between users, protection against enumeration attacks.

#### Rate Limiting

**Configuration**: 100 requests/hour per authenticated user, Redis-backed for distributed systems.

**Impact**: API stability under load, protection against abuse, fair resource allocation.

### Testing

**Requirement**: 80%+ coverage on business logic (services layer).

**Strategy**: 
- Comprehensive test suites in `apps/auth/tests/` and `apps/notes/tests/`
- pytest-django for Django-aware testing
- HTML coverage reports for visual gap analysis

**Impact**: Confidence in refactoring, tests serve as documentation, catch regressions before deployment.

**Run tests**: `make dev-test-cov`

### Deployment & DevOps

#### Docker Multi-Stage Builds

**Files**: [`backend/Dockerfile`](backend/Dockerfile) (production), [`backend/Dockerfile.dev`](backend/Dockerfile.dev) (development)

**Impact**: Development/production parity, reproducible builds, smaller production images, consistent environments across team.

#### 12-Factor App Compliance

I implemented **all 12 factors** to demonstrate production-grade systems expertise:

1. **Codebase**: Single repo, multiple deploys
2. **Dependencies**: Explicit in `pyproject.toml` with Poetry
3. **Config**: Environment variables via django-environ
4. **Backing Services**: PostgreSQL, Redis as attached resources
5. **Build, Release, Run**: Separate Docker stages
6. **Processes**: Stateless, share-nothing (horizontally scalable)
7. **Port Binding**: Self-contained service exports HTTP
8. **Concurrency**: Gunicorn workers + Celery workers
9. **Disposability**: Fast startup, graceful shutdown
10. **Dev/Prod Parity**: Docker ensures consistency
11. **Logs**: Stream to stdout (12-factor compliant)
12. **Admin Processes**: Django management commands in containers

**Impact**: Cloud-native, horizontally scalable, deployable to any platform (AWS, GCP, Heroku, etc.).

#### Makefile Automation

[`Makefile`](Makefile) with 30+ commands for common workflows.

**Examples**: `make dev-up`, `make dev-test-cov`, `make dev-migrate`, `make prod-up`

**Impact**: Faster onboarding, consistent workflows across team, reduced human error.

### Code Quality

#### Linting & Formatting

**Tools**: Black (formatting), Ruff (linting) configured in [`backend/pyproject.toml`](backend/pyproject.toml)

**Impact**: Zero style debates, automated consistency, catch bugs before runtime.

#### Split Settings Pattern

**Files**: `base.py` (shared), `development.py` (debug mode), `production.py` (secure defaults)

**Impact**: Environment-specific optimizations without duplication, easier secret management.

## Frontend

### Technology Stack

#### Next.js 16 + React 19 + TypeScript

**Why**: Modern React framework with built-in optimizations, server-side rendering capabilities, and excellent developer experience. TypeScript ensures type safety across the codebase.

**Impact**: Fast page loads, automatic code splitting, built-in API routes, hot module replacement for instant feedback during development.

#### Tailwind CSS 4

**Why**: Utility-first CSS framework enables rapid UI development without leaving the markup. Version 4 brings performance improvements and modern CSS features.

**Impact**: Consistent design system, reduced CSS bundle size, faster development velocity.

#### Bun Package Manager

**Why**: Significantly faster package installation and script execution compared to npm/yarn (3-10x in benchmarks).

**Impact**: Faster builds, reduced CI/CD time, improved developer experience with instant feedback.

### Containerization

#### Docker Development & Production Setup

**Development**:
- Hot reload with Next.js Fast Refresh
- Volume mounting for instant code changes
- Optimized for macOS with `:cached` mount flags
- Separate from production build for faster feedback

**Production**:
- Multi-stage Docker build for minimal image size
- Next.js standalone mode reduces image to ~72MB (compressed)
- Non-root user for security
- Health check endpoint at `/api/health`

**Files**: [`frontend/Dockerfile`](frontend/Dockerfile) (production), [`frontend/Dockerfile.dev`](frontend/Dockerfile.dev) (development)

**Impact**: Development/production parity, consistent environments, optimized production deployment, seamless hot reload during development.

### Architecture & Security

#### Network Isolation

**Strategy**: Frontend container can only communicate with backend API via Docker network. No direct access to PostgreSQL or Redis.

**Implementation**: Docker Compose configures frontend service on `noteapp_network` with dependencies only on `api` service. Database and cache ports not exposed to frontend.

**Impact**: Defense in depth, reduced attack surface, enforces proper API-based architecture.

#### Environment Configuration

**Variables**:
- `NEXT_PUBLIC_API_URL`: Backend API endpoint (defaults: `http://localhost:8000` dev, `http://api:8000` prod)
- `NODE_ENV`: Environment mode (development/production)

**Impact**: Flexible deployment configurations, environment-specific optimizations, client-side API discovery.

## Quick Start

### Development Environment

```bash
# Start all services (backend + frontend + databases)
docker-compose -f docker-compose.dev.yml up

# Or start in detached mode
docker-compose -f docker-compose.dev.yml up -d

# View services
docker-compose -f docker-compose.dev.yml ps

# Access services
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/api/docs/

# View logs
docker-compose -f docker-compose.dev.yml logs frontend
docker-compose -f docker-compose.dev.yml logs api

# Stop all services
docker-compose -f docker-compose.dev.yml down

# Run backend tests with coverage
make dev-test-cov
```

### Production Environment

```bash
# Build and start all services
docker-compose up -d

# View service status
docker-compose ps

# View logs
docker-compose logs frontend
docker-compose logs api

# Stop all services
docker-compose down
```

### Hot Reload (Development)

The frontend is configured with volume mounting for instant hot reload:

1. Edit any file in `frontend/app/` or `frontend/components/`
2. Save the file
3. Next.js Fast Refresh automatically updates the browser (no rebuild needed)
4. Check logs: `docker-compose -f docker-compose.dev.yml logs frontend`

If hot reload isn't working on macOS, set this environment variable:

```bash
echo "WATCHPACK_POLLING=true" >> .env
docker-compose -f docker-compose.dev.yml restart frontend
```

### Troubleshooting

**Frontend can't reach backend:**
```bash
# Check if API service is healthy
docker-compose -f docker-compose.dev.yml ps api

# Check backend logs
docker-compose -f docker-compose.dev.yml logs api

# Verify network connectivity from frontend
docker exec -it noteapp_frontend_dev sh
wget -O- http://api:8000/api/health/
```

**Port already in use:**
```bash
# Stop conflicting services
docker-compose -f docker-compose.dev.yml down

# Or change ports in docker-compose.dev.yml
# Edit the ports section: "3001:3000" instead of "3000:3000"
```

**Slow file watching on macOS:**
- This is a known Docker limitation on macOS
- The `:cached` flag in docker-compose.dev.yml already optimizes this
- If still slow, use `WATCHPACK_POLLING=true` (trades CPU for consistency)

See [`backend/README.md`](backend/README.md) for comprehensive API documentation.

## Repository Structure

```
noteapp/
├── backend/              # Django REST Framework API
│   ├── api/              # Django project config
│   ├── apps/             # Applications (auth, notes)
│   ├── tests/            # 80%+ coverage test suite
│   ├── Dockerfile        # Production Docker build
│   └── Dockerfile.dev    # Development Docker build with hot reload
├── frontend/             # Next.js 16 + React 19 application
│   ├── app/              # App router pages and API routes
│   ├── public/           # Static assets
│   ├── Dockerfile        # Production Docker build (standalone mode)
│   └── Dockerfile.dev    # Development Docker build with hot reload
├── docker-compose.yml    # Production orchestration (frontend + backend + databases)
├── docker-compose.dev.yml # Development with hot reload for both frontend and backend
└── Makefile              # 30+ automation commands
```