# Feature Specification: User Authentication

**Feature:** User Authentication & Authorization
**Priority:** P0 (Critical - MVP)
**Status:** Specification Phase
**Last Updated:** 2025-12-31

---

## 1. Overview

### Feature Description
Users can create accounts, log in securely, and access their personal data. Authentication is required for all task operations. Each user can only access their own tasks.

### User Story
**As a** new user
**I want to** create an account and log in
**So that** I can securely store and access my personal tasks

### Success Criteria
- [ ] Users can sign up with email and password
- [ ] Users can log in with email and password
- [ ] Users can log out
- [ ] Passwords are securely hashed
- [ ] JWT tokens are used for authentication
- [ ] Protected routes require authentication
- [ ] Users can only access their own data

---

## 2. Requirements

### 2.1 User Signup (FR-040)

**Requirement:** Users can create new accounts

**Acceptance Criteria:**
- AC1: User provides name, email, and password
- AC2: Email must be valid format
- AC3: Email must be unique (not already registered)
- AC4: Password must be at least 8 characters
- AC5: Password is hashed before storage (bcrypt)
- AC6: User receives JWT token on successful signup
- AC7: User is automatically logged in after signup

**Input Validation:**
```typescript
interface SignupInput {
  name: string       // Required, min 2 characters
  email: string      // Required, valid email format
  password: string   // Required, min 8 characters
}
```

**Validation Rules:**
- Name: 2-100 characters
- Email: Valid email format (RFC 5322)
- Password: Minimum 8 characters
- All fields required

**Error Cases:**
- Email already exists → `"Error: Email already registered."`
- Invalid email format → `"Error: Invalid email address."`
- Password too short → `"Error: Password must be at least 8 characters."`
- Missing fields → `"Error: All fields are required."`

### 2.2 User Login (FR-041)

**Requirement:** Users can log in with credentials

**Acceptance Criteria:**
- AC1: User provides email and password
- AC2: Email and password are verified
- AC3: Password hash is compared securely
- AC4: JWT token generated on success
- AC5: Token includes user_id in 'sub' claim
- AC6: Token expiry set to 7 days
- AC7: Token stored in httpOnly cookie

**Input Validation:**
```typescript
interface LoginInput {
  email: string
  password: string
}
```

**Error Cases:**
- Email not found → `"Error: Invalid email or password."`
- Wrong password → `"Error: Invalid email or password."`
- Account locked → `"Error: Account temporarily locked."`

**Security Note:** Use same error message for "email not found" and "wrong password" to prevent email enumeration.

### 2.3 User Logout (FR-042)

**Requirement:** Users can log out securely

**Acceptance Criteria:**
- AC1: User clicks "Logout" button
- AC2: JWT token is invalidated
- AC3: Cookie is cleared
- AC4: User redirected to login page
- AC5: Protected routes become inaccessible

### 2.4 JWT Token Management (FR-043)

**Requirement:** Secure token-based authentication

**JWT Token Structure:**
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user-id-here",
    "email": "user@example.com",
    "name": "User Name",
    "iat": 1735689600,
    "exp": 1736294400
  },
  "signature": "..."
}
```

**Acceptance Criteria:**
- AC1: Token signed with BETTER_AUTH_SECRET
- AC2: Token includes user_id in 'sub' claim
- AC3: Token expires in 7 days
- AC4: Token verified on every protected request
- AC5: Expired tokens return 401 Unauthorized
- AC6: Invalid tokens return 401 Unauthorized

### 2.5 Protected Routes (FR-044)

**Requirement:** Authentication required for task operations

**Protected Routes:**
- `/tasks` - Task list page
- `/tasks/new` - Create task page
- `/tasks/[id]` - Task detail page
- `/profile` - User profile page
- All API endpoints (except `/api/auth/*`)

**Acceptance Criteria:**
- AC1: Unauthenticated users redirected to `/login`
- AC2: JWT token verified before page render
- AC3: API endpoints verify token in middleware
- AC4: Invalid/expired token returns 401

### 2.6 Authorization (FR-045)

**Requirement:** Users can only access their own data

**Authorization Rules:**
- User can only read their own tasks
- User can only create tasks for themselves
- User can only update their own tasks
- User can only delete their own tasks
- URL user_id must match token user_id

**Acceptance Criteria:**
- AC1: Every API endpoint verifies user_id match
- AC2: Mismatch returns 403 Forbidden
- AC3: Database queries filter by user_id
- AC4: Users cannot see other users' data

**Enforcement:**
```python
# Backend enforcement
if url_user_id != token_user_id:
    raise HTTPException(status_code=403, detail="Forbidden")

# Database query enforcement
tasks = await session.execute(
    select(Task).where(Task.user_id == token_user_id)
)
```

---

## 3. User Flows

### 3.1 Signup Flow

```
1. User visits landing page
2. User clicks "Sign Up"
3. User fills signup form (name, email, password)
4. Frontend validates input
5. Frontend sends POST /api/auth/signup
6. Backend validates data
7. Backend checks email uniqueness
8. Backend hashes password (bcrypt)
9. Backend creates user in database
10. Backend generates JWT token
11. Backend returns user + token
12. Frontend stores token in httpOnly cookie
13. Frontend redirects to /tasks
```

### 3.2 Login Flow

```
1. User visits /login page
2. User enters email and password
3. Frontend validates input
4. Frontend sends POST /api/auth/login
5. Backend finds user by email
6. Backend verifies password hash
7. Backend generates JWT token
8. Backend returns user + token
9. Frontend stores token in httpOnly cookie
10. Frontend redirects to /tasks
```

### 3.3 Logout Flow

```
1. User clicks "Logout" button
2. Frontend sends POST /api/auth/logout
3. Backend invalidates session (if applicable)
4. Frontend clears auth cookie
5. Frontend redirects to /login
```

### 3.4 Protected Route Access

```
1. User navigates to /tasks
2. Middleware checks for JWT token
3. Token found → verify signature
4. Token valid → extract user_id
5. Pass user_id to page
6. Page renders with user data

OR

3. Token missing/invalid → redirect to /login
```

---

## 4. API Endpoints

### 4.1 Signup

```http
POST /api/auth/signup
Content-Type: application/json

Request:
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}

Response (201 Created):
{
  "user": {
    "id": "user-uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2025-12-31T12:00:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 4.2 Login

```http
POST /api/auth/login
Content-Type: application/json

Request:
{
  "email": "john@example.com",
  "password": "securepassword123"
}

Response (200 OK):
{
  "user": {
    "id": "user-uuid",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 4.3 Logout

```http
POST /api/auth/logout
Authorization: Bearer <jwt_token>

Response (200 OK):
{
  "message": "Logged out successfully"
}
```

### 4.4 Get Session

```http
GET /api/auth/session
Authorization: Bearer <jwt_token>

Response (200 OK):
{
  "user": {
    "id": "user-uuid",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

---

## 5. Database Schema

```sql
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_users_email ON users(email);
```

---

## 6. Security Considerations

### Password Security
- ✅ Passwords hashed with bcrypt (cost factor: 10)
- ✅ Passwords never stored in plain text
- ✅ Passwords never logged
- ✅ Password requirements enforced

### Token Security
- ✅ JWT signed with strong secret (BETTER_AUTH_SECRET)
- ✅ Token stored in httpOnly cookie (XSS protection)
- ✅ SameSite=Strict (CSRF protection)
- ✅ Secure flag in production (HTTPS only)
- ✅ Token expiry enforced

### Authorization Security
- ✅ Every endpoint verifies authentication
- ✅ Every endpoint verifies authorization
- ✅ User_id from token, never from client input
- ✅ Database queries filter by user_id

---

## 7. Frontend Components

### UI Components Needed
- `LoginForm.tsx` - Login form
- `SignupForm.tsx` - Signup form
- `LogoutButton.tsx` - Logout button
- `AuthProvider.tsx` - Auth context provider
- `ProtectedRoute.tsx` - Route wrapper

See: `@specs/ui/components.md` for detailed component specs

---

## 8. Backend Components

### Files Needed
- `app/routers/auth.py` - Auth endpoints
- `app/middleware/auth.py` - JWT verification
- `app/dependencies/auth.py` - Auth dependencies
- `app/models.py` - User model
- `app/schemas.py` - Auth schemas

See: `@backend/CLAUDE.md` for implementation guide

---

## 9. Environment Variables

```bash
# Shared secret for JWT signing (min 32 characters)
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters

# CORS allowed origins
CORS_ORIGINS=http://localhost:3000

# Database URL
DATABASE_URL=postgresql+asyncpg://...
```

---

## 10. Testing Requirements

### Unit Tests
- [ ] Password hashing
- [ ] JWT token generation
- [ ] JWT token verification
- [ ] Email validation
- [ ] Password validation

### Integration Tests
- [ ] Signup with valid data
- [ ] Signup with duplicate email
- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Logout clears session
- [ ] Protected routes require auth
- [ ] Token expiry handling
- [ ] User_id authorization

---

## 11. Error Messages

```
"Error: Email already registered."
"Error: Invalid email address."
"Error: Password must be at least 8 characters."
"Error: All fields are required."
"Error: Invalid email or password."
"Error: Token has expired."
"Error: Invalid token."
"Error: Unauthorized."
"Error: Forbidden."
```

---

## Related Specifications

- `@specs/api/auth-endpoints.md` - Auth API details
- `@specs/database/users-table.md` - Users table schema
- `@specs/ui/components.md` - Auth UI components
- `@frontend/CLAUDE.md` - Frontend auth guide
- `@backend/CLAUDE.md` - Backend auth guide

---

**Document Type:** Feature Specification (WHAT)
**Lifecycle Stage:** Specify
**Status:** Ready for Implementation
**Priority:** P0 (Critical)
