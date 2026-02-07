# UI Specification: Components

**Document:** Component Library Specification
**Framework:** Next.js 16+ + TypeScript + Tailwind CSS
**Last Updated:** 2025-12-31

---

## Overview

Specification for all reusable React components in the application.

---

## Component Hierarchy

```
components/
├── ui/                          # Generic UI components
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Card.tsx
│   ├── Modal.tsx
│   └── Badge.tsx
│
├── features/                    # Feature-specific components
│   ├── tasks/
│   │   ├── TaskList.tsx        # Server component
│   │   ├── TaskItem.tsx        # Client component
│   │   ├── TaskForm.tsx        # Client component
│   │   ├── TaskFilters.tsx     # Client component
│   │   └── DeleteConfirmation.tsx
│   └── auth/
│       ├── LoginForm.tsx       # Client component
│       ├── SignupForm.tsx      # Client component
│       └── LogoutButton.tsx    # Client component
│
└── layout/                      # Layout components
    ├── Header.tsx              # Client component
    ├── Sidebar.tsx             # Client component (future)
    └── Footer.tsx              # Server component
```

---

## Generic UI Components

### Button

**File:** `components/ui/Button.tsx`
**Type:** Client component

**Props:**
```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'destructive'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  onClick?: () => void
  children: React.ReactNode
}
```

**Variants:**
- `primary` - Main actions (blue background)
- `secondary` - Secondary actions (gray background)
- `outline` - Outlined button
- `destructive` - Dangerous actions (red background)

---

### Input

**File:** `components/ui/Input.tsx`
**Type:** Client component

**Props:**
```typescript
interface InputProps {
  type?: 'text' | 'email' | 'password'
  placeholder?: string
  value?: string
  onChange?: (value: string) => void
  error?: string
  disabled?: boolean
}
```

**Features:**
- Error state styling
- Disabled state
- Label support

---

### Card

**File:** `components/ui/Card.tsx`
**Type:** Server component

**Props:**
```typescript
interface CardProps {
  children: React.ReactNode
  className?: string
}
```

**Styling:**
- White background
- Rounded corners
- Shadow
- Padding

---

## Task Components

### TaskList

**File:** `components/features/tasks/TaskList.tsx`
**Type:** Server component

**Props:**
```typescript
interface TaskListProps {
  tasks: Task[]
}
```

**Behavior:**
- Displays array of tasks
- Uses `TaskItem` for each task
- Shows empty state if no tasks

---

### TaskItem

**File:** `components/features/tasks/TaskItem.tsx`
**Type:** Client component

**Props:**
```typescript
interface TaskItemProps {
  task: Task
  onUpdate?: (taskId: string) => void
  onDelete?: (taskId: string) => void
}
```

**Features:**
- Complete/incomplete toggle
- Edit button
- Delete button
- Priority indicator
- Tags display

---

### TaskForm

**File:** `components/features/tasks/TaskForm.tsx`
**Type:** Client component

**Props:**
```typescript
interface TaskFormProps {
  taskId?: string           // If editing existing task
  initialData?: TaskInput
  onSuccess?: () => void
}
```

**Fields:**
- Title (required)
- Description (optional)
- Priority (select)
- Tags (input)

**Validation:**
- Zod schema validation
- Error display

---

## Auth Components

### LoginForm

**File:** `components/features/auth/LoginForm.tsx`
**Type:** Client component

**Fields:**
- Email (required)
- Password (required)

**Features:**
- Form validation
- Error messages
- Submit button

---

### SignupForm

**File:** `components/features/auth/SignupForm.tsx`
**Type:** Client component

**Fields:**
- Name (required)
- Email (required)
- Password (required)

**Features:**
- Form validation
- Error messages
- Submit button

---

## Layout Components

### Header

**File:** `components/layout/Header.tsx`
**Type:** Client component

**Features:**
- App logo/name
- Navigation links
- User menu
- Logout button

---

## Component Guidelines

### TypeScript Types
All components must have proper TypeScript interfaces.

### Styling
Use Tailwind CSS utility classes only.

### Server vs Client
- Use server components by default
- Mark client components with `'use client'`

### Error Handling
All interactive components must handle errors gracefully.

---

## Related Specifications

- `@specs/ui/pages.md` - Page specifications
- `@frontend/CLAUDE.md` - Frontend implementation guide

---

**Document Type:** UI Component Specification
**Status:** Ready for Implementation
**Priority:** P0 (Critical)
