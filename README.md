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

## Frontend (Future)

**Status**: Not yet implemented.

**Reflection**: Developer experience could be better with either:
1. Monorepo with same-language full-stack (e.g., Node.js + Next.js)
2. Separate repositories for backend and frontend

**Current Reality**: Python backend + future JavaScript frontend in same repo makes proper monorepo tooling (shared configs, unified scripts) challenging.

**When Built**: Will consume the Django REST API with JWT authentication, implement note CRUD and category management.

## Quick Start

```bash
# Start development environment
make dev-up-d

# View API docs
open http://localhost:8000/api/docs/

# Run tests with coverage
make dev-test-cov

# View logs
make dev-logs-api
```

See [`backend/README.md`](backend/README.md) for comprehensive API documentation.

## Repository Structure

```
noteapp/
├── backend/              # Django REST Framework API
│   ├── api/              # Django project config
│   ├── apps/             # Applications (auth, notes)
│   └── tests/            # 80%+ coverage test suite
├── docker-compose.yml    # Production orchestration
├── docker-compose.dev.yml # Development with hot reload
└── Makefile              # 30+ automation commands
```