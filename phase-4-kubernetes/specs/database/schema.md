# Database Schema Specification

**Database:** PostgreSQL (Neon Serverless)
**ORM:** SQLModel (async)
**Driver:** asyncpg
**Last Updated:** 2025-12-31

---

## Overview

Complete database schema for the Todo Manager application. This document defines all tables, relationships, indexes, and constraints.

---

## Schema Diagram

```
┌─────────────────────────────────────┐
│            users                    │
├─────────────────────────────────────┤
│ id                VARCHAR PK        │
│ name              VARCHAR NOT NULL  │
│ email             VARCHAR UNIQUE    │
│ hashed_password   VARCHAR NOT NULL  │
│ created_at        TIMESTAMP         │
│ updated_at        TIMESTAMP         │
└─────────────────────────────────────┘
            │
            │ 1
            │
            │ ∞
┌─────────────────────────────────────┐
│            tasks                    │
├─────────────────────────────────────┤
│ id                VARCHAR PK        │
│ title             VARCHAR(200)      │
│ description       VARCHAR(1000)     │
│ completed         BOOLEAN           │
│ priority          VARCHAR(10)       │
│ tags              TEXT              │
│ recurrence_pattern VARCHAR(10)     │
│ recurrence_interval INTEGER        │
│ due_date          TIMESTAMP         │
│ user_id           VARCHAR FK        │
│ created_at        TIMESTAMP         │
│ updated_at        TIMESTAMP         │
└─────────────────────────────────────┘
```

---

## Tables

### users
See: `@specs/database/users-table.md`

### tasks
See: `@specs/database/todos-table.md`

---

## Relationships

### users → tasks (One-to-Many)

```sql
ALTER TABLE tasks
ADD CONSTRAINT fk_tasks_user_id
FOREIGN KEY (user_id)
REFERENCES users(id)
ON DELETE CASCADE;
```

**Cascade Behavior:**
- Deleting a user deletes all their tasks
- This ensures data consistency
- User cleanup removes all associated data

---

## Indexes

### users table

```sql
CREATE UNIQUE INDEX idx_users_email ON users(email);
```

**Purpose:** Fast user lookup by email (login)

### tasks table

```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
```

**Purpose:**
- `idx_tasks_user_id`: Fast task queries per user
- `idx_tasks_completed`: Filter by completion status
- `idx_tasks_priority`: Sort/filter by priority
- `idx_tasks_due_date`: Sort/filter by due date, find overdue tasks

---

## Constraints

### users table

- `id`: PRIMARY KEY
- `email`: UNIQUE, NOT NULL
- `name`: NOT NULL
- `hashed_password`: NOT NULL

### tasks table

- `id`: PRIMARY KEY
- `title`: NOT NULL, max 200 characters
- `description`: max 1000 characters
- `completed`: DEFAULT FALSE
- `priority`: DEFAULT 'Medium', CHECK (priority IN ('High', 'Medium', 'Low'))
- `user_id`: FOREIGN KEY → users(id), ON DELETE CASCADE

---

## Data Types

### UUID Strings
```sql
id VARCHAR PRIMARY KEY
```

**Rationale:** Using VARCHAR for UUIDs to maintain compatibility and simplicity.

### Timestamps
```sql
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**Rationale:** UTC timestamps for consistency across time zones.

### Text Fields
```sql
title VARCHAR(200)
description VARCHAR(1000)
tags TEXT
```

**Rationale:** VARCHAR for length-limited fields, TEXT for unlimited.

---

## Migrations

### Initial Migration

```sql
-- Create users table
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Create tasks table
CREATE TABLE tasks (
    id VARCHAR PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    completed BOOLEAN DEFAULT FALSE,
    priority VARCHAR(10) DEFAULT 'Medium'
        CHECK (priority IN ('High', 'Medium', 'Low')),
    tags TEXT DEFAULT '',
    recurrence_pattern VARCHAR(10) DEFAULT NULL
        CHECK (recurrence_pattern IN ('Daily', 'Weekly', 'Monthly', NULL)),
    recurrence_interval INTEGER DEFAULT 1
        CHECK (recurrence_interval > 0),
    due_date TIMESTAMP DEFAULT NULL,
    user_id VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
```

### Using Alembic

```bash
# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## Sample Data

### users

| id | name | email | hashed_password | created_at |
|----|------|-------|-----------------|------------|
| user-1 | John Doe | john@example.com | $2b$10$... | 2025-12-31 12:00:00 |
| user-2 | Jane Smith | jane@example.com | $2b$10$... | 2025-12-31 12:05:00 |

### tasks

| id | title | description | completed | priority | tags | user_id | created_at |
|----|-------|-------------|-----------|----------|------|---------|------------|
| task-1 | Write docs | Complete API specs | false | High | documentation,urgent | user-1 | 2025-12-31 12:10:00 |
| task-2 | Review code | Check PR #42 | true | Medium | review | user-1 | 2025-12-31 12:15:00 |

---

## Performance Considerations

- **Indexes:** All foreign keys and frequently queried fields indexed
- **Connection Pooling:** SQLModel + asyncpg handles connection pooling
- **Query Optimization:** Always filter by user_id for security and performance
- **Serverless Scaling:** Neon automatically scales connections

---

## Security Considerations

- **Password Hashing:** Passwords hashed with bcrypt before storage
- **User Isolation:** All queries filter by user_id
- **Cascade Deletes:** User deletion removes all associated data
- **Input Validation:** Enforced at application layer (Pydantic)

---

## Related Specifications

- `@specs/database/users-table.md` - Users table details
- `@specs/database/todos-table.md` - Tasks table details
- `@specs/architecture.md` - System architecture
- `@backend/CLAUDE.md` - Backend implementation

---

**Document Type:** Database Schema Specification
**Status:** Ready for Implementation
**Priority:** P0 (Critical)
