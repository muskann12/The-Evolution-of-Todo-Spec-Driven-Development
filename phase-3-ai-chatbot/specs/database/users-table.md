# Database Table Specification: users

**Table Name:** `users`
**Purpose:** Store user account information
**Last Updated:** 2025-12-31

---

## Table Definition

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

## Columns

### id
- **Type:** VARCHAR
- **Constraints:** PRIMARY KEY
- **Description:** Unique user identifier (UUID format)
- **Example:** `"550e8400-e29b-41d4-a716-446655440000"`

### name
- **Type:** VARCHAR(100)
- **Constraints:** NOT NULL
- **Description:** User's display name
- **Validation:** 2-100 characters
- **Example:** `"John Doe"`

### email
- **Type:** VARCHAR(255)
- **Constraints:** UNIQUE, NOT NULL
- **Description:** User's email address (used for login)
- **Validation:** Valid email format (RFC 5322)
- **Example:** `"john@example.com"`

### hashed_password
- **Type:** VARCHAR(255)
- **Constraints:** NOT NULL
- **Description:** Bcrypt hashed password
- **Format:** `$2b$10$...` (bcrypt hash)
- **Example:** `"$2b$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy"`

### created_at
- **Type:** TIMESTAMP
- **Constraints:** DEFAULT CURRENT_TIMESTAMP
- **Description:** Account creation timestamp (UTC)
- **Example:** `"2025-12-31T12:00:00Z"`

### updated_at
- **Type:** TIMESTAMP
- **Constraints:** DEFAULT CURRENT_TIMESTAMP
- **Description:** Last update timestamp (UTC)
- **Example:** `"2025-12-31T14:30:00Z"`

---

## Indexes

### Primary Key
```sql
PRIMARY KEY (id)
```

### Unique Email Index
```sql
CREATE UNIQUE INDEX idx_users_email ON users(email);
```

**Purpose:** Fast user lookup by email (login queries)

---

## Relationships

### users → tasks (One-to-Many)

One user can have many tasks.

```sql
SELECT * FROM tasks WHERE user_id = 'user-uuid';
```

---

## Sample Data

```sql
INSERT INTO users (id, name, email, hashed_password, created_at, updated_at)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'John Doe',
    'john@example.com',
    '$2b$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy',
    '2025-12-31 12:00:00',
    '2025-12-31 12:00:00'
);
```

---

## SQLModel Definition

```python
from datetime import datetime
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User model for authentication."""

    __tablename__ = "users"

    id: str = Field(primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Queries

### Create User
```python
async def create_user(session: AsyncSession, user_data: UserCreate) -> User:
    user = User(
        id=str(uuid.uuid4()),
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
```

### Find User by Email
```python
async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    return result.scalar_one_or_none()
```

---

## Related Specifications

- `@specs/features/user-authentication.md` - Auth feature spec
- `@specs/api/auth-endpoints.md` - Auth API endpoints
- `@specs/database/schema.md` - Complete schema

---

**Document Type:** Database Table Specification
**Status:** Ready for Implementation
**Priority:** P0 (Critical)
