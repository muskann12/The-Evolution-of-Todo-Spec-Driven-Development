# UI Specification: Pages

**Document:** Page Specifications
**Framework:** Next.js 16+ (App Router)
**Last Updated:** 2025-12-31

---

## Overview

This document specifies all pages/routes in the application using Next.js App Router conventions.

---

## Route Structure

```
app/
├── layout.tsx                    # Root layout
├── page.tsx                      # Home/landing page
│
├── (auth)/                       # Auth route group (no layout)
│   ├── login/
│   │   └── page.tsx             # Login page
│   └── signup/
│       └── page.tsx             # Signup page
│
└── (dashboard)/                  # Protected route group
    ├── layout.tsx               # Dashboard layout
    ├── tasks/
    │   ├── page.tsx            # Task list page
    │   ├── [id]/
    │   │   └── page.tsx        # Task detail page
    │   └── new/
    │       └── page.tsx        # Create task page
    └── profile/
        └── page.tsx            # User profile page
```

---

## Pages

### 1. Home Page (`/`)

**File:** `app/page.tsx`
**Auth:** Public
**Type:** Server component

**Purpose:** Landing page for unauthenticated users

**Content:**
- Hero section with app description
- Call-to-action buttons (Login, Sign Up)
- Feature highlights
- If logged in: redirect to `/tasks`

---

### 2. Login Page (`/login`)

**File:** `app/(auth)/login/page.tsx`
**Auth:** Public (redirects to `/tasks` if logged in)
**Type:** Client component

**Purpose:** User authentication

**Components:**
- `LoginForm` - Email/password form
- Link to signup page
- Error messages

**Behavior:**
- On success: redirect to `/tasks`
- On failure: show error message

---

### 3. Signup Page (`/signup`)

**File:** `app/(auth)/signup/page.tsx`
**Auth:** Public (redirects to `/tasks` if logged in)
**Type:** Client component

**Purpose:** New user registration

**Components:**
- `SignupForm` - Name/email/password form
- Link to login page
- Error messages

**Behavior:**
- On success: redirect to `/tasks`
- On failure: show error message

---

### 4. Tasks List Page (`/tasks`)

**File:** `app/(dashboard)/tasks/page.tsx`
**Auth:** Protected
**Type:** Server component

**Purpose:** Display all user's tasks

**Components:**
- `TaskList` - List of tasks
- `TaskFilters` - Filter/sort controls
- "New Task" button

**Data Fetching:**
```tsx
const tasks = await api.getTasks(userId)
```

---

### 5. Task Detail Page (`/tasks/[id]`)

**File:** `app/(dashboard)/tasks/[id]/page.tsx`
**Auth:** Protected
**Type:** Server component

**Purpose:** View single task details

**Components:**
- `TaskDetail` - Full task information
- Edit/Delete buttons
- Back to list link

**Data Fetching:**
```tsx
const task = await api.getTask(userId, taskId)
```

---

### 6. Create Task Page (`/tasks/new`)

**File:** `app/(dashboard)/tasks/new/page.tsx`
**Auth:** Protected
**Type:** Client component

**Purpose:** Create new task

**Components:**
- `TaskForm` - Create task form
- Cancel button

**Behavior:**
- On success: redirect to `/tasks`
- On cancel: redirect to `/tasks`

---

### 7. User Profile Page (`/profile`)

**File:** `app/(dashboard)/profile/page.tsx`
**Auth:** Protected
**Type:** Server component (Future)
**Status:** Post-MVP

**Purpose:** User profile management

**Components:**
- User information display
- Edit profile form (future)
- Change password form (future)

---

## Related Specifications

- `@specs/ui/components.md` - UI components
- `@specs/ui/layouts.md` - Layout specifications
- `@frontend/CLAUDE.md` - Frontend implementation guide

---

**Document Type:** UI Specification
**Status:** Ready for Implementation
**Priority:** P0 (Critical)
