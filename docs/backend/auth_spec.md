# Backend Technical Spec: Authentication Service

## 1. Architectural Strategy

The authentication system is implemented using a **Service-Layer Pattern**. This decouples the REST interface (Views) from the business logic, allowing for easier unit testing, maintainability, and future integration with additional authentication providers (e.g., OAuth2, social login).

The architecture follows a strict separation of concerns:
- **Views** (`views.py`): Handle HTTP requests/responses, input validation via serializers
- **Serializers** (`serializers.py`): Validate and transform request/response data
- **Services** (`services.py`): Contain all business logic (user creation, authentication, token management)
- **Authentication Backend** (`authentication.py`): Custom JWT authentication with blacklist checking
- **Throttles** (`throttles.py`): Rate limiting implementation using Redis

## 2. Data Schema & Persistence (PostgreSQL)

The User model extends Django's `AbstractUser` and uses email as the primary authentication identifier.

| Field | Type | Storage Strategy | Notes |
| --- | --- | --- | --- |
| `id` | `BigInt` | Primary Key | Auto-incrementing integer ID. |
| `email` | `EmailField` | Unique Index | Primary identifier for authentication. Normalized to lowercase. |
| `username` | `CharField(150)` | Unique Index | Auto-generated from email if not provided. Not used for authentication. |
| `password` | `CharField` | Hashed | Stored using Django's PBKDF2 hashing algorithm. |
| `is_active` | `BooleanField` | Default: True | Controls whether user can authenticate. |
| `is_staff` | `BooleanField` | Default: False | Admin access flag. |
| `is_superuser` | `BooleanField` | Default: False | Superuser access flag. |
| `created_at` | `DateTimeField` | Auto-created | Timestamp of user registration. |
| `updated_at` | `DateTimeField` | Auto-updated | Timestamp of last user update. |

**Key Design Decisions:**
- Email is the `USERNAME_FIELD` (not username)
- Username is auto-generated from email prefix if not provided, ensuring uniqueness
- Email is normalized to lowercase before storage and lookup
- Password validation uses Django's built-in validators (minimum length 8, common password checks, etc.)

## 3. API Contract & Implementation Details

### 3.1 Endpoint Architecture

All authentication endpoints are versioned via Accept header (`Accept: application/vnd.noteapp.v1+json`) but also accept standard `application/json` for backward compatibility.

#### `POST /api/auth/signup` (User Registration)

* **Permission:** Public (no authentication required)
* **Input Validation:**
  - Email: Must be valid email format, normalized to lowercase
  - Password: Must pass Django's password validators (min 8 chars, not common password, etc.)
* **Service Layer:** `auth_service.register_user(email, password)`
* **Business Logic:**
  1. Normalize email to lowercase and trim whitespace
  2. Check for existing user with same email (raises `ValidationError` if exists)
  3. Create user with hashed password (transaction-wrapped)
  4. Trigger background Celery task `initialize_user_environment` for user setup
* **Response:** `201 Created` with user data (id, email, created_at) - **no tokens returned on signup**
* **Error Responses:**
  - `400 Bad Request`: Invalid email format, weak password, or duplicate email
  - `429 Too Many Requests`: Rate limit exceeded (20 requests/hour per IP for anonymous)

#### `POST /api/auth/signin` (User Authentication)

* **Permission:** Public (no authentication required)
* **Input Validation:**
  - Email: Must be valid email format, normalized to lowercase
  - Password: Required string
* **Service Layer:** `auth_service.authenticate_user(email, password)`
* **Business Logic:**
  1. Normalize email to lowercase and trim whitespace
  2. Lookup user by email (raises `AuthenticationFailed` if not found)
  3. Verify password using Django's `check_password()` (raises `AuthenticationFailed` if invalid)
  4. Check if user is active (raises `AuthenticationFailed` if disabled)
  5. Generate JWT tokens using `RefreshToken.for_user(user)`
* **Response:** `200 OK` with tokens:
  ```json
  {
    "access_token": "eyJ0eXAiOiJKV1Qi...",
    "refresh_token": "eyJ0eXAiOiJKV1Qi...",
    "token_type": "Bearer"
  }
  ```
* **Error Responses:**
  - `401 Unauthorized`: Invalid credentials or inactive account
  - `429 Too Many Requests`: Rate limit exceeded

#### `POST /api/auth/refresh` (Token Refresh)

* **Permission:** Public (no authentication required)
* **Input Validation:**
  - `refresh_token`: Required string, must be valid JWT
* **Service Layer:** `auth_service.refresh_access_token(refresh_token)`
* **Business Logic:**
  1. Validate refresh token structure and signature
  2. Check token expiration
  3. Generate new access token from refresh token
  4. If token rotation enabled (`ROTATE_REFRESH_TOKENS=True`), generate new refresh token and blacklist old one
* **Response:** `200 OK` with new tokens (access_token always, refresh_token if rotation enabled)
* **Error Responses:**
  - `401 Unauthorized`: Invalid, expired, or blacklisted refresh token
  - `429 Too Many Requests`: Rate limit exceeded

#### `POST /api/auth/logout` (User Logout)

* **Permission:** Authenticated (requires valid access token)
* **Input Validation:**
  - `refresh_token`: Required string, must be valid JWT
* **Service Layer:** `auth_service.logout_user(refresh_token)`
* **Business Logic:**
  1. Validate refresh token structure and signature
  2. Extract JTI (JWT ID) from token
  3. Calculate remaining token lifetime
  4. Store JTI in Redis blacklist with TTL matching token expiration
  5. Key format: `blacklist:jti:{jti}` with value `"1"`
* **Response:** `200 OK` with message:
  ```json
  {
    "message": "Successfully logged out"
  }
  ```
* **Error Responses:**
  - `401 Unauthorized`: Invalid access token or invalid refresh token
  - `400 Bad Request`: Missing refresh_token in request body
  - `429 Too Many Requests`: Rate limit exceeded

#### `GET /api/auth/me` (Current User Info)

* **Permission:** Authenticated (requires valid access token)
* **Service Layer:** Direct serializer usage (no service layer needed)
* **Business Logic:**
  1. Extract user from authenticated request (`request.user`)
  2. Serialize user data
* **Response:** `200 OK` with user data:
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "first_name": "",
    "last_name": "",
    "created_at": "2024-01-01T12:00:00Z"
  }
  ```
* **Error Responses:**
  - `401 Unauthorized`: Missing or invalid access token
  - `429 Too Many Requests`: Rate limit exceeded

## 4. JWT Token Management

### 4.1 Token Configuration

| Setting | Value | Notes |
| --- | --- | --- |
| `ACCESS_TOKEN_LIFETIME` | 15 minutes (default) | Configurable via `JWT_ACCESS_TOKEN_LIFETIME` env var |
| `REFRESH_TOKEN_LIFETIME` | 7 days (10080 minutes, default) | Configurable via `JWT_REFRESH_TOKEN_LIFETIME` env var |
| `ROTATE_REFRESH_TOKENS` | `True` | New refresh token issued on each refresh |
| `BLACKLIST_AFTER_ROTATION` | `True` | Old refresh token blacklisted after rotation |
| `ALGORITHM` | `HS256` | HMAC with SHA-256 |
| `SIGNING_KEY` | `SECRET_KEY` | Uses Django's SECRET_KEY |
| `AUTH_HEADER_TYPES` | `("Bearer",)` | OAuth2-compliant format |

### 4.2 Token Structure

Tokens are OAuth2-compliant JWTs with the following claims:
- `user_id`: User's database ID
- `exp`: Token expiration timestamp
- `jti`: JWT ID (unique identifier for blacklist tracking)
- `token_type`: Token type ("access" or "refresh")
- Standard JWT claims (iat, exp, etc.)

### 4.3 Token Blacklist Implementation

The system uses a **Redis-based blacklist** to revoke tokens before expiration:

* **Storage:** Redis cache (db 0)
* **Key Format:** `blacklist:jti:{jti_value}`
* **Value:** `"1"` (presence indicates blacklisted)
* **TTL:** Matches remaining token lifetime (calculated from token expiration)

**Blacklist Checking Flow:**
1. Custom authentication backend `BlacklistCheckingJWTAuthentication` extends `JWTAuthentication`
2. On each authenticated request:
   - Extract JTI from validated token
   - Check Redis for `blacklist:jti:{jti}` key
   - If key exists, raise `AuthenticationFailed("Token has been revoked")`
3. Blacklist is checked for **access tokens** during authentication
4. Refresh tokens are blacklisted on logout or rotation

## 5. Security & Business Rules

### 5.1 Password Security

* **Validation:** Uses Django's built-in password validators:
  - `UserAttributeSimilarityValidator`: Prevents similarity to user attributes
  - `MinimumLengthValidator`: Minimum 8 characters
  - `CommonPasswordValidator`: Rejects common passwords
  - `NumericPasswordValidator`: Prevents entirely numeric passwords
* **Storage:** Passwords are hashed using PBKDF2 with SHA-256 (Django default)
* **Never Returned:** Passwords are never included in API responses

### 5.2 Email Normalization

* **Rule:** All emails are normalized to lowercase and trimmed before storage/lookup
* **Implementation:** Applied in both serializers and service layer
* **Benefit:** Prevents duplicate accounts with case variations (e.g., `User@Example.com` vs `user@example.com`)

### 5.3 Rate Limiting

The system implements **distributed rate limiting** using Redis:

| Throttle Type | Scope | Default Limit | Configurable Via |
| --- | --- | --- | --- |
| `UserRateThrottle` | Per authenticated user | 100 requests/hour | `RATE_LIMIT_USER_HOUR` env var |
| `AnonRateThrottle` | Per IP address | 20 requests/hour | `RATE_LIMIT_ANON_HOUR` env var |

**Implementation Details:**
* Uses Redis cache backend for distributed systems (multiple server instances)
* Cache key format: `throttle_{scope}_{ident}_{scope}`
* For authenticated users: `throttle_user_{user_id}_user`
* For anonymous users: `throttle_anon_{ip_address}_anon`
* Rate limits apply to all endpoints by default (can be overridden per view)

### 5.4 Account Security

* **Active Check:** Inactive users (`is_active=False`) cannot authenticate
* **Error Message:** Returns generic "Invalid credentials" to prevent user enumeration
* **Token Revocation:** Logged-out tokens are immediately blacklisted and cannot be reused

### 5.5 Multi-Tenant Isolation

All user-related queries are scoped by `user_id`:
* User lookup: `User.objects.get(email=email)`
* Token generation: `RefreshToken.for_user(user)` includes user_id in claims
* Authentication: Token validation includes user lookup and verification

## 6. API Versioning

The API supports **Accept Header Versioning** for backward compatibility:

* **Format:** `Accept: application/vnd.noteapp.v1+json`
* **Default Version:** `v1` (if no version specified)
* **Allowed Versions:** `["v1"]`
* **Backward Compatibility:** Standard `Accept: application/json` also accepted

**Implementation:**
* Custom content negotiation class: `VendorContentNegotiation`
* Normalizes vendor media types to `application/json` for renderer selection
* All endpoints support versioned headers

## 7. Background Tasks (Celery)

### 7.1 User Environment Initialization

On user registration, a background Celery task is triggered:

* **Task:** `initialize_user_environment(user_id)`
* **Trigger:** Automatically called after successful user creation
* **Retry Logic:** 3 retries with 60-second delay between attempts
* **Purpose:** Initialize user-specific data structures, default configurations, and workspace setup

**Current Implementation:**
* Placeholder task (TODO: implement actual initialization logic)
* Logs initialization start/completion
* Returns status dictionary with user_id, email, and status

### 7.2 Celery Configuration

* **Broker:** Redis (db 1)
* **Result Backend:** Redis (db 0)
* **Task Serialization:** JSON
* **Time Limit:** 30 minutes per task
* **Task Tracking:** Enabled

## 8. Logic Flows

### 8.1 Registration Flow

```
1. Client sends POST /api/auth/signup with {email, password}
2. Serializer validates email format and password strength
3. Service normalizes email (lowercase, trim)
4. Service checks for existing user → raises ValidationError if exists
5. Service creates user with hashed password (transaction-wrapped)
6. Service triggers Celery task initialize_user_environment.delay(user.id)
7. Response: 201 Created with {id, email, created_at}
```

### 8.2 Authentication Flow

```
1. Client sends POST /api/auth/signin with {email, password}
2. Serializer validates email format
3. Service normalizes email (lowercase, trim)
4. Service looks up user by email → raises AuthenticationFailed if not found
5. Service verifies password → raises AuthenticationFailed if invalid
6. Service checks is_active flag → raises AuthenticationFailed if disabled
7. Service generates JWT tokens (RefreshToken.for_user(user))
8. Response: 200 OK with {access_token, refresh_token, token_type}
```

### 8.3 Token Refresh Flow

```
1. Client sends POST /api/auth/refresh with {refresh_token}
2. Serializer validates refresh_token presence
3. Service validates token structure and signature
4. Service checks token expiration
5. Service generates new access token
6. If ROTATE_REFRESH_TOKENS=True:
   a. Generate new refresh token
   b. Blacklist old refresh token (if BLACKLIST_AFTER_ROTATION=True)
7. Response: 200 OK with {access_token, refresh_token (if rotated), token_type}
```

### 8.4 Logout Flow

```
1. Client sends POST /api/auth/logout with {refresh_token}
   (Requires valid access token in Authorization header)
2. Custom authentication backend validates access token:
   a. Extracts token from Authorization: Bearer header
   b. Validates JWT structure and signature
   c. Checks blacklist in Redis
   d. Looks up user from token claims
3. Serializer validates refresh_token presence
4. Service validates refresh token structure
5. Service extracts JTI from refresh token
6. Service calculates remaining token lifetime
7. Service stores JTI in Redis: blacklist:jti:{jti} with TTL = remaining_seconds
8. Response: 200 OK with {message: "Successfully logged out"}
```

### 8.5 Request Authentication Flow

```
1. Client sends request with Authorization: Bearer {access_token}
2. Custom authentication backend (BlacklistCheckingJWTAuthentication):
   a. Extracts token from Authorization header
   b. Validates JWT structure, signature, and expiration
   c. Extracts JTI from token
   d. Checks Redis blacklist: cache.get("blacklist:jti:{jti}")
   e. If blacklisted → raises AuthenticationFailed("Token has been revoked")
   f. Looks up user from token user_id claim
   g. Returns (user, validated_token) tuple
3. Permission classes check authentication status
4. View processes request with request.user available
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
| `400 Bad Request` | Invalid input, duplicate email, weak password | Validation error details |
| `401 Unauthorized` | Invalid credentials, inactive account, revoked token | "Invalid credentials" or "Token has been revoked" |
| `429 Too Many Requests` | Rate limit exceeded | Standard DRF throttle error |

### 9.3 Security Considerations

* **User Enumeration Prevention:** Authentication errors return generic "Invalid credentials" message
* **Token Security:** Tokens are never logged or exposed in error messages
* **Password Security:** Password validation errors don't reveal password requirements in detail
