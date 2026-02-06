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

**Backend**: Django REST Framework API with Service Layer architecture, OAuth2-compliant JWT authentication with Redis blacklist, PostgreSQL 16 with UUID primary keys, Redis for caching and rate limiting, Celery background tasks, 80%+ test coverage, full 12-factor app compliance, and multi-tenant data isolation with security-first design.

**Frontend**: Next.js 16 + React 19 + TypeScript application with Tailwind CSS 4, Bun package manager, Docker multi-stage builds (separate dev/prod configurations), network isolation architecture, and environment-based configuration for flexible deployment.

**Infrastructure**: Production-ready Docker containerization with multi-stage builds, Makefile automation with 30+ commands, development/production parity, and cloud-native deployment ready for any platform.

## Backend

### Key Highlights

- Service Layer architecture pattern separates business logic from HTTP handling for testability and reusability
- Django REST Framework + Python 3.12 with PostgreSQL 16 and Redis for caching and rate limiting
- JWT authentication with Redis blacklist enables stateless tokens with proper logout capability
- 80%+ test coverage on business logic using pytest-django with comprehensive test suites
- Full 12-factor app compliance with Docker multi-stage builds and Makefile automation for cloud-native deployment
- Multi-tenant data isolation with security-first design prevents ID enumeration attacks
- Celery background tasks offload long-running operations from request/response cycle

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

I chose Django REST Framework for its mature ecosystem and batteries-included approach, enabling rapid development without sacrificing robustness. Built-in admin, ORM security, and extensive middleware reduce boilerplate while automatically preventing SQL injection. The framework's maturity means instant admin panels and battle-tested patterns for production use.

#### Database & Caching: PostgreSQL 16 + Redis

I selected PostgreSQL 16 for JSONB support, robust ACID transactions, and excellent performance at scale. UUID primary keys prevent ID enumeration attacks, enhancing security while better suiting distributed systems.

Redis handles three critical use cases: JWT blacklist for instant token revocation (sub-millisecond validation), distributed rate limiting across API instances, and category note counts cache with atomic increments and 1-hour TTL, reducing database queries by 90%+.

#### Celery Background Tasks

I implemented Celery to offload long-running operations from the request/response cycle. For example, the `initialize_user_environment` task runs asynchronously after signup to create default categories without blocking the HTTP response. This delivers faster API responses, better user experience, and resilient async processing with automatic retries.

### Security Architecture

I implemented a multi-layered security approach combining stateless JWT benefits with proper logout capability. My custom `BlacklistCheckingJWTAuthentication` checks Redis before accepting tokens, ensuring blacklisted tokens remain invalid even if not expired—critical for production applications despite adding a Redis dependency.

- **Multi-tenant isolation**: All database queries strictly scoped by `user_id` with 404 responses (not 403) for non-existent resources to prevent ID enumeration attacks, ensuring complete data isolation between users
- **Rate limiting**: 100 requests/hour per authenticated user, Redis-backed for distributed systems, providing API stability under load and protection against abuse

### Testing

I achieved 80%+ test coverage on business logic (services layer) using comprehensive test suites in `apps/auth/tests/` and `apps/notes/tests/` with pytest-django for Django-aware testing. HTML coverage reports enable visual gap analysis, providing confidence in refactoring, serving as documentation, and catching regressions before deployment.

### Deployment & DevOps

#### Docker Multi-Stage Builds

I implemented separate Docker configurations for development and production. **Files**: [`backend/Dockerfile`](backend/Dockerfile) (production), [`backend/Dockerfile.dev`](backend/Dockerfile.dev) (development). This ensures development/production parity, reproducible builds, smaller production images, and consistent environments across team.

#### 12-Factor App Compliance

I implemented **all 12 factors** to demonstrate production-grade systems expertise, ensuring the application is cloud-native, horizontally scalable, and deployable to any platform (AWS, GCP, Heroku, etc.).

**Code & Dependencies**: Single repo with multiple deploys, explicit dependencies in `pyproject.toml` with Poetry, environment variables via django-environ

**Services & Build**: PostgreSQL and Redis as attached backing services, separate Docker stages for build/release/run, stateless share-nothing processes for horizontal scalability

**Runtime & Operations**: Self-contained service exports HTTP, Gunicorn workers + Celery workers for concurrency, fast startup with graceful shutdown, Docker ensures dev/prod parity, logs stream to stdout, Django management commands run in containers

#### Makefile Automation

I created a [`Makefile`](Makefile) with 30+ commands for common workflows (examples: `make dev-up`, `make dev-test-cov`, `make dev-migrate`, `make prod-up`). This enables faster onboarding, consistent workflows across team, and reduced human error.

### Code Quality

I configured Black (formatting) and Ruff (linting) in [`backend/pyproject.toml`](backend/pyproject.toml) for automated consistency and catching bugs before runtime. I implemented a split settings pattern with `base.py` (shared), `development.py` (debug mode), and `production.py` (secure defaults) to enable environment-specific optimizations without duplication and easier secret management.

## Frontend

### Key Highlights

- Next.js 16 + React 19 + TypeScript for modern React framework with built-in optimizations and type safety
- Tailwind CSS 4 utility-first approach enables rapid UI development with consistent design system
- Bun package manager delivers 3-10x faster package installation and script execution
- Docker multi-stage builds with separate dev/prod configurations optimize for each environment (~72MB production image)
- Network isolation architecture ensures frontend only communicates with backend API, enforcing proper security boundaries

### Technology Stack

I chose Next.js 16 with React 19 for built-in optimizations, server-side rendering, and excellent developer experience. Next.js provides automatic code splitting, built-in API routes, and server components out of the box, while React 19 brings improved concurrent features and better performance. TypeScript ensures type safety across the entire frontend codebase, catching type errors at compile time to prevent runtime bugs. This combination delivers fast page loads, reduced bundle sizes, and hot module replacement for instant development feedback.

I adopted Tailwind CSS 4 for rapid UI development without leaving the markup. The utility-first approach eliminates context switching between CSS files and components, while version 4 brings significant performance improvements and modern CSS features. Utility classes enable consistent design system enforcement directly in markup, reducing custom CSS files and resulting in smaller bundle sizes through purging unused styles.

I selected Bun over npm/yarn for dramatically faster package installation and script execution (3-10x faster in benchmarks). Bun's JavaScript runtime written in Zig provides near-instant package resolution and script execution, reducing CI/CD pipeline time and improving developer experience with instant feedback.

### Containerization

#### Docker Multi-Stage Builds

I implemented separate Docker configurations for development and production to optimize for each environment's needs. **Files**: [`frontend/Dockerfile`](frontend/Dockerfile) (production), [`frontend/Dockerfile.dev`](frontend/Dockerfile.dev) (development)

**Development**: Hot reload with Next.js Fast Refresh, volume mounting with `:cached` flags optimized for macOS, separate Dockerfile to avoid production build overhead.

**Production**: Multi-stage Docker build minimizes final image size, Next.js standalone mode reduces production image to ~72MB (compressed), non-root user execution for security, health check endpoint at `/api/health` for container orchestration.

This ensures development/production parity, consistent environments across team members, optimized production deployment, and seamless hot reload during development.

### Architecture & Security

I designed the frontend container to communicate exclusively with the backend API via Docker network, with no direct access to PostgreSQL or Redis. Docker Compose configures the frontend service on `noteapp_network` with dependencies only on the `api` service, intentionally not exposing database and cache ports. This defense-in-depth approach ensures that even if the frontend is compromised, attackers cannot directly access database or cache, enforcing proper API-based architecture where all data access flows through authenticated endpoints.

I implemented environment-based configuration using Next.js's built-in environment variable system. The `NEXT_PUBLIC_API_URL` variable (defaults: `http://localhost:8000` dev, `http://api:8000` prod) enables client-side API discovery without hardcoded URLs, allowing flexible deployment configurations and seamless switching between local development and containerized environments.
