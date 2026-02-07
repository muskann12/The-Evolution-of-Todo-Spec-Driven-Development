# API Specification: Authentication Endpoints

**API Group:** Authentication & Authorization
**Base Path:** `/api/auth`
**Authentication:** Public (signup/login), Protected (logout/session)
**Last Updated:** 2025-12-31

---

## Overview

Authentication endpoints for user signup, login, logout, and session management using JWT tokens.

---

## Endpoints

### 1. Signup

**POST** `/api/auth/signup`

Create a new user account.

**Request:**
```http
POST /api/auth/signup HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (201 Created):**
```json
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

**Validation:**
- `name`: Required, 2-100 characters
- `email`: Required, valid email format, unique
- `password`: Required, min 8 characters

**Error Responses:**
- `400 Bad Request` - Validation failed
- `409 Conflict` - Email already exists

---

### 2. Login

**POST** `/api/auth/login`

Authenticate user and receive JWT token.

**Request:**
```http
POST /api/auth/login HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "user-uuid",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials

---

### 3. Logout

**POST** `/api/auth/logout`

Log out current user.

**Request:**
```http
POST /api/auth/logout HTTP/1.1
Host: localhost:8000
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "message": "Logged out successfully"
}
```

---

### 4. Get Session

**GET** `/api/auth/session`

Get current user session.

**Request:**
```http
GET /api/auth/session HTTP/1.1
Host: localhost:8000
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "user-uuid",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

---

## Related Specifications

- `@specs/features/user-authentication.md` - Auth feature spec
- `@specs/database/users-table.md` - Users table schema

---

**Document Type:** API Specification
**Status:** Ready for Implementation
**Priority:** P0 (Critical)
