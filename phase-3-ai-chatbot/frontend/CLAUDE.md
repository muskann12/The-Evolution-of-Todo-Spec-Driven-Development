# Claude Code Guide - Next.js Frontend

This document provides **Next.js-specific guidance** for Claude Code when working on the frontend of the Phase II-III Web Application (including AI Chatbot).

**IMPORTANT:** Always read the main navigation guide first: `@../CLAUDE.md`

---

## 1. STACK

### Technology Stack

**Phase II:**
- **Next.js 16+** (App Router)
- **TypeScript** (strict mode enabled)
- **Tailwind CSS** (utility-first styling)
- **Better Auth** (authentication & authorization)
- **React Query** (server state management)
- **Zod** (runtime validation)

**Phase III (AI Chatbot):**
- **OpenAI ChatKit** (Pre-built AI chat interface components)

### Version Requirements

```json
{
  "next": "^16.0.0",
  "react": "^19.0.0",
  "typescript": "^5.3.0",
  "tailwindcss": "^3.4.0",
  "better-auth": "latest"
}
```

### Development Environment

- **Node.js**: 18.x or higher
- **Package Manager**: npm (default) or pnpm
- **Port**: http://localhost:3000 (development)
- **API Backend**: http://localhost:8000 (FastAPI)

---

## 2. PATTERNS

### Key Development Patterns

#### 1. Server Components by Default

```tsx
// ✅ GOOD - Server component (default)
// app/tasks/page.tsx
export default async function TasksPage() {
  // Fetch data directly in server component
  const tasks = await getTasks()

  return (
    <div>
      <TaskList tasks={tasks} />
    </div>
  )
}
```

**Use server components for:**
- Static pages
- Data fetching
- SEO-critical content
- Layout components

#### 2. Client Components When Needed

```tsx
// ✅ GOOD - Client component for interactivity
// components/TaskForm.tsx
'use client'

import { useState } from 'react'

export function TaskForm() {
  const [title, setTitle] = useState('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    // Handle form submission
  }

  return <form onSubmit={handleSubmit}>...</form>
}
```

**Use client components for:**
- Forms and input handling
- Interactive UI (clicks, hovers, animations)
- Browser APIs (localStorage, window, etc.)
- State management with useState/useReducer
- Event handlers

#### 3. API Calls Through Centralized Client

```tsx
// ✅ GOOD - Use centralized API client
import { api } from '@/lib/api'

const tasks = await api.getTasks(userId)
const newTask = await api.createTask({ title, description })
```

```tsx
// ❌ BAD - Direct fetch calls
const response = await fetch('http://localhost:8000/api/tasks')
```

#### 4. Forms and Interactive Elements

```tsx
// ✅ GOOD - Client component for forms
'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { taskSchema } from '@/lib/validation'

export function TaskForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(taskSchema)
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('title')} />
      {errors.title && <span>{errors.title.message}</span>}
    </form>
  )
}
```

---

## 3. PROJECT STRUCTURE

### Folder Organization

```
frontend/
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── (auth)/                   # Auth route group
│   │   │   ├── login/
│   │   │   │   └── page.tsx         # Login page
│   │   │   └── signup/
│   │   │       └── page.tsx         # Signup page
│   │   ├── (dashboard)/              # Protected route group
│   │   │   ├── tasks/
│   │   │   │   ├── page.tsx         # Tasks list page
│   │   │   │   ├── [id]/
│   │   │   │   │   └── page.tsx     # Task detail page
│   │   │   │   └── new/
│   │   │   │       └── page.tsx     # Create task page
│   │   │   ├── chat/
│   │   │   │   └── page.tsx         # AI chat interface (Phase III)
│   │   │   └── layout.tsx           # Dashboard layout
│   │   ├── api/                      # API routes (if needed)
│   │   │   └── auth/                # Better Auth routes
│   │   ├── layout.tsx                # Root layout
│   │   ├── page.tsx                  # Home page
│   │   └── globals.css               # Global styles
│   │
│   ├── components/                   # Reusable UI components
│   │   ├── ui/                       # Generic UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   └── Modal.tsx
│   │   ├── features/                 # Feature-specific components
│   │   │   ├── tasks/
│   │   │   │   ├── TaskList.tsx
│   │   │   │   ├── TaskItem.tsx
│   │   │   │   ├── TaskForm.tsx
│   │   │   │   └── TaskFilters.tsx
│   │   │   └── auth/
│   │   │       ├── LoginForm.tsx
│   │   │       ├── SignupForm.tsx
│   │   │       └── LogoutButton.tsx
│   │   ├── layout/                   # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   └── providers/                # Context providers
│   │       ├── AuthProvider.tsx
│   │       └── QueryProvider.tsx
│   │
│   ├── lib/                          # Utility functions and helpers
│   │   ├── api.ts                    # API client for backend calls
│   │   ├── auth.ts                   # Better Auth configuration
│   │   ├── types.ts                  # TypeScript type definitions
│   │   ├── validation.ts             # Zod schemas
│   │   ├── utils.ts                  # General utilities
│   │   └── constants.ts              # App constants
│   │
│   └── styles/                       # Additional styles
│       └── globals.css               # Global CSS with Tailwind
│
├── public/                           # Static assets
│   ├── favicon.ico
│   ├── images/
│   └── fonts/
│
├── tests/                            # Frontend tests
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   └── e2e/                          # End-to-end tests
│
├── .env.local                        # Environment variables (gitignored)
├── .env.example                      # Example environment variables
├── next.config.js                    # Next.js configuration
├── tailwind.config.js                # Tailwind CSS configuration
├── tsconfig.json                     # TypeScript configuration
├── package.json                      # Dependencies
├── CLAUDE.md                         # This file
└── README.md                         # Frontend documentation
```

### Key Directories

#### `/app` - Pages and Layouts (App Router)
- **File-based routing** - Folders create routes
- **page.tsx** - Defines a route's UI
- **layout.tsx** - Shared UI for multiple pages
- **loading.tsx** - Loading UI with React Suspense
- **error.tsx** - Error UI boundary
- **Route groups** - Organize routes with `(group-name)`

#### `/components` - Reusable UI Components
- **ui/** - Generic, reusable UI primitives (Button, Input, Card)
- **features/** - Feature-specific components (TaskList, LoginForm)
- **layout/** - Layout components (Header, Sidebar, Footer)
- **providers/** - React context providers

#### `/lib` - Utility Functions and API Client
- **api.ts** - Centralized API client for backend calls
- **auth.ts** - Better Auth configuration
- **types.ts** - TypeScript interfaces and types
- **validation.ts** - Zod schemas for runtime validation
- **utils.ts** - Helper functions (cn, formatDate, etc.)

---

## 4. API CLIENT

### Centralized API Client

All backend API calls **MUST** use the centralized API client located at `/lib/api.ts`.

#### API Client Implementation

```typescript
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include', // Include cookies for auth
    })

    if (response.status === 401) {
      // Unauthorized - redirect to login
      window.location.href = '/login'
      throw new Error('Unauthorized')
    }

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || 'API request failed')
    }

    return response.json()
  }

  // Tasks API
  async getTasks(userId: string): Promise<Task[]> {
    return this.request<Task[]>(`/api/tasks?user_id=${userId}`)
  }

  async getTask(taskId: string): Promise<Task> {
    return this.request<Task>(`/api/tasks/${taskId}`)
  }

  async createTask(data: CreateTaskInput): Promise<Task> {
    return this.request<Task>('/api/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateTask(taskId: string, data: UpdateTaskInput): Promise<Task> {
    return this.request<Task>(`/api/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async deleteTask(taskId: string): Promise<void> {
    return this.request<void>(`/api/tasks/${taskId}`, {
      method: 'DELETE',
    })
  }

  // Auth API
  async login(email: string, password: string): Promise<AuthResponse> {
    return this.request<AuthResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
  }

  async logout(): Promise<void> {
    return this.request<void>('/api/auth/logout', {
      method: 'POST',
    })
  }
}

export const api = new ApiClient(API_BASE_URL)
```

#### Usage Examples

```tsx
// ✅ GOOD - Use API client
import { api } from '@/lib/api'

// In a server component
export default async function TasksPage() {
  const tasks = await api.getTasks(userId)
  return <TaskList tasks={tasks} />
}

// In a client component
'use client'
import { api } from '@/lib/api'

export function TaskForm() {
  const handleSubmit = async (data: CreateTaskInput) => {
    try {
      const newTask = await api.createTask(data)
      console.log('Task created:', newTask)
    } catch (error) {
      console.error('Failed to create task:', error)
    }
  }

  return <form onSubmit={handleSubmit}>...</form>
}
```

### API Client Features

The API client automatically:
- ✅ **Attaches JWT tokens** from cookies (credentials: 'include')
- ✅ **Handles authentication errors** (401 redirects to /login)
- ✅ **Sets proper headers** (Content-Type: application/json)
- ✅ **Parses JSON responses** automatically
- ✅ **Throws errors** for failed requests
- ✅ **Type-safe** with TypeScript generics

---

## 5. COMPONENT GUIDELINES

### Feature Components

#### TaskList - Display All Tasks

```tsx
// components/features/tasks/TaskList.tsx
'use client'

import { Task } from '@/lib/types'
import { TaskItem } from './TaskItem'

interface TaskListProps {
  tasks: Task[]
  onTaskUpdate?: (taskId: string) => void
  onTaskDelete?: (taskId: string) => void
}

export function TaskList({ tasks, onTaskUpdate, onTaskDelete }: TaskListProps) {
  if (tasks.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No tasks found. Create your first task!
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onUpdate={onTaskUpdate}
          onDelete={onTaskDelete}
        />
      ))}
    </div>
  )
}
```

#### TaskItem - Individual Task Card

```tsx
// components/features/tasks/TaskItem.tsx
'use client'

import { Task } from '@/lib/types'
import { Button } from '@/components/ui/Button'
import { api } from '@/lib/api'

interface TaskItemProps {
  task: Task
  onUpdate?: (taskId: string) => void
  onDelete?: (taskId: string) => void
}

export function TaskItem({ task, onUpdate, onDelete }: TaskItemProps) {
  const handleComplete = async () => {
    await api.updateTask(task.id, { completed: !task.completed })
    onUpdate?.(task.id)
  }

  const handleDelete = async () => {
    await api.deleteTask(task.id)
    onDelete?.(task.id)
  }

  return (
    <div className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className={`text-lg font-semibold ${task.completed ? 'line-through text-gray-500' : ''}`}>
            {task.title}
          </h3>
          {task.description && (
            <p className="mt-2 text-gray-600">{task.description}</p>
          )}
        </div>
        <div className="flex gap-2 ml-4">
          <Button onClick={handleComplete} variant="outline" size="sm">
            {task.completed ? 'Undo' : 'Complete'}
          </Button>
          <Button onClick={handleDelete} variant="destructive" size="sm">
            Delete
          </Button>
        </div>
      </div>
    </div>
  )
}
```

#### TaskForm - Add/Edit Task

```tsx
// components/features/tasks/TaskForm.tsx
'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { taskSchema, type TaskInput } from '@/lib/validation'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'

interface TaskFormProps {
  taskId?: string
  initialData?: TaskInput
  onSuccess?: () => void
}

export function TaskForm({ taskId, initialData, onSuccess }: TaskFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<TaskInput>({
    resolver: zodResolver(taskSchema),
    defaultValues: initialData,
  })

  const onSubmit = async (data: TaskInput) => {
    try {
      if (taskId) {
        await api.updateTask(taskId, data)
      } else {
        await api.createTask(data)
      }
      onSuccess?.()
    } catch (error) {
      console.error('Failed to save task:', error)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Input
          {...register('title')}
          placeholder="Task title"
          error={errors.title?.message}
        />
      </div>
      <div>
        <textarea
          {...register('description')}
          placeholder="Task description (optional)"
          className="w-full rounded-md border p-2"
          rows={4}
        />
        {errors.description && (
          <span className="text-sm text-red-500">{errors.description.message}</span>
        )}
      </div>
      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Saving...' : taskId ? 'Update Task' : 'Create Task'}
      </Button>
    </form>
  )
}
```

#### Header - Navigation with User Info

```tsx
// components/layout/Header.tsx
'use client'

import Link from 'next/link'
import { useAuth } from '@/lib/auth'
import { Button } from '@/components/ui/Button'
import { api } from '@/lib/api'

export function Header() {
  const { user, isAuthenticated } = useAuth()

  const handleLogout = async () => {
    await api.logout()
    window.location.href = '/login'
  }

  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-gray-900">
            Todo App
          </Link>

          <nav className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                <Link href="/tasks" className="text-gray-700 hover:text-gray-900">
                  Tasks
                </Link>
                <Link href="/chat" className="text-gray-700 hover:text-gray-900">
                  Chat
                </Link>
                <span className="text-gray-600">Hello, {user?.name}</span>
                <Button onClick={handleLogout} variant="outline">
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link href="/login">
                  <Button variant="outline">Login</Button>
                </Link>
                <Link href="/signup">
                  <Button>Sign Up</Button>
                </Link>
              </>
            )}
          </nav>
        </div>
      </div>
    </header>
  )
}
```

#### LoginForm - Email/Password Authentication

```tsx
// components/features/auth/LoginForm.tsx
'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { loginSchema, type LoginInput } from '@/lib/validation'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useRouter } from 'next/navigation'

export function LoginForm() {
  const router = useRouter()
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginInput>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (data: LoginInput) => {
    try {
      await api.login(data.email, data.password)
      router.push('/tasks')
    } catch (error) {
      console.error('Login failed:', error)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Input
          {...register('email')}
          type="email"
          placeholder="Email"
          error={errors.email?.message}
        />
      </div>
      <div>
        <Input
          {...register('password')}
          type="password"
          placeholder="Password"
          error={errors.password?.message}
        />
      </div>
      <Button type="submit" disabled={isSubmitting} className="w-full">
        {isSubmitting ? 'Logging in...' : 'Login'}
      </Button>
    </form>
  )
}
```

---

## 6. STYLING

### Tailwind CSS Guidelines

#### Use Utility Classes Only

```tsx
// ✅ GOOD - Tailwind utilities
<div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
  <h2 className="text-2xl font-bold text-gray-900">Title</h2>
  <p className="mt-2 text-gray-600">Description</p>
</div>
```

```tsx
// ❌ BAD - Inline styles
<div style={{ backgroundColor: 'white', padding: '24px' }}>
  <h2 style={{ fontSize: '24px', fontWeight: 'bold' }}>Title</h2>
</div>
```

#### Follow Existing Component Patterns

```tsx
// Button variants pattern
<Button variant="primary">Save</Button>
<Button variant="outline">Cancel</Button>
<Button variant="destructive">Delete</Button>

// Input with error state
<Input
  placeholder="Email"
  error={errors.email?.message}
/>
```

#### Responsive Design (Mobile-First)

```tsx
// ✅ GOOD - Mobile-first responsive design
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Cards */}
</div>

<div className="text-sm md:text-base lg:text-lg">
  Responsive text
</div>
```

#### Common Tailwind Patterns

```tsx
// Container
<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

// Card
<div className="bg-white rounded-lg shadow-md p-6">

// Form spacing
<form className="space-y-4">

// Button group
<div className="flex gap-2">

// Centered content
<div className="flex items-center justify-center min-h-screen">

// Grid layout
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
```

---

## 7. AUTHENTICATION

### Better Auth Integration

#### Better Auth Configuration

```typescript
// lib/auth.ts
import { BetterAuth } from 'better-auth'

export const auth = new BetterAuth({
  database: {
    provider: 'postgres',
    url: process.env.DATABASE_URL!,
  },
  emailAndPassword: {
    enabled: true,
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
  },
})

export const { signIn, signOut, signUp, useSession } = auth
```

#### Auth Flow

1. **Signup** - User creates account with email/password
2. **Login** - User logs in, receives JWT token stored in httpOnly cookie
3. **Protected Routes** - Middleware checks authentication
4. **API Requests** - Automatically include credentials (cookies)
5. **Logout** - Clear session and redirect to login

#### Protected Routes with Middleware

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token')

  // Protect /tasks and other authenticated routes
  if (request.nextUrl.pathname.startsWith('/tasks')) {
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/tasks/:path*', '/profile/:path*'],
}
```

#### Using Authentication in Components

```tsx
// Server component
import { auth } from '@/lib/auth'

export default async function TasksPage() {
  const session = await auth.api.getSession()

  if (!session) {
    redirect('/login')
  }

  return <div>Welcome, {session.user.name}!</div>
}

// Client component
'use client'
import { useSession } from '@/lib/auth'

export function UserProfile() {
  const { data: session, status } = useSession()

  if (status === 'loading') return <div>Loading...</div>
  if (!session) return <div>Not authenticated</div>

  return <div>Hello, {session.user.name}!</div>
}
```

### JWT Tokens in httpOnly Cookies

- **Storage:** Tokens stored in httpOnly cookies (not accessible via JavaScript)
- **Security:** Prevents XSS attacks
- **Automatic:** API client includes credentials automatically
- **Expiry:** Tokens expire after 7 days (configurable)

---

## 8. TYPE SAFETY

### TypeScript Strict Mode

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true
  }
}
```

### Type Definitions

```typescript
// lib/types.ts

// Task types
export interface Task {
  id: string
  title: string
  description: string | null
  completed: boolean
  priority: 'High' | 'Medium' | 'Low'
  tags: string[]
  userId: string
  createdAt: string
  updatedAt: string
}

export interface CreateTaskInput {
  title: string
  description?: string
  priority?: 'High' | 'Medium' | 'Low'
  tags?: string[]
}

export interface UpdateTaskInput {
  title?: string
  description?: string
  completed?: boolean
  priority?: 'High' | 'Medium' | 'Low'
  tags?: string[]
}

// User types
export interface User {
  id: string
  name: string
  email: string
  createdAt: string
}

export interface AuthResponse {
  user: User
  token: string
}

export interface LoginInput {
  email: string
  password: string
}

export interface SignupInput {
  name: string
  email: string
  password: string
}
```

### Validation Schemas

```typescript
// lib/validation.ts
import { z } from 'zod'

export const taskSchema = z.object({
  title: z.string()
    .min(1, 'Title is required')
    .max(200, 'Title must be less than 200 characters'),
  description: z.string()
    .max(1000, 'Description must be less than 1000 characters')
    .optional(),
  priority: z.enum(['High', 'Medium', 'Low']).default('Medium'),
  tags: z.array(z.string()).default([]),
})

export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
})

export const signupSchema = loginSchema.extend({
  name: z.string().min(2, 'Name must be at least 2 characters'),
})

export type TaskInput = z.infer<typeof taskSchema>
export type LoginInput = z.infer<typeof loginSchema>
export type SignupInput = z.infer<typeof signupSchema>
```

### Type Safety Rules

- ✅ **All components typed** with interfaces
- ✅ **No 'any' types** allowed (use unknown if needed)
- ✅ **Import types** from `/lib/types.ts`
- ✅ **Use Zod** for runtime validation
- ✅ **Type API responses** with generics
- ✅ **Null checks** required (strictNullChecks: true)

```tsx
// ✅ GOOD - Properly typed
interface TaskItemProps {
  task: Task
  onUpdate?: (taskId: string) => void
}

export function TaskItem({ task, onUpdate }: TaskItemProps) {
  // TypeScript knows exact shape of task
  return <div>{task.title}</div>
}

// ❌ BAD - Using 'any'
export function TaskItem({ task }: any) {
  return <div>{task.title}</div> // No type safety
}
```

---

## 9. DEVELOPMENT WORKFLOW

### Step-by-Step Implementation

#### Step 1: Read Specification
```bash
# Read UI spec before implementing
@../specs/ui/components.md
@../specs/ui/pages.md
```

#### Step 2: Create Component
```bash
# Follow naming convention
components/features/tasks/TaskList.tsx
```

#### Step 3: Implement with Types
```tsx
// 1. Import types
import { Task } from '@/lib/types'

// 2. Define props interface
interface TaskListProps {
  tasks: Task[]
}

// 3. Implement component
export function TaskList({ tasks }: TaskListProps) {
  // Implementation
}
```

#### Step 4: Add Styling
```tsx
// Use Tailwind utilities
<div className="bg-white rounded-lg shadow p-6">
  {/* Content */}
</div>
```

#### Step 5: Test Component
```bash
npm test components/features/tasks/TaskList.test.tsx
```

---

## 10. COMMON PATTERNS

### Data Fetching in Server Components

```tsx
// app/tasks/page.tsx
import { api } from '@/lib/api'
import { TaskList } from '@/components/features/tasks/TaskList'

export default async function TasksPage() {
  const tasks = await api.getTasks()

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">My Tasks</h1>
      <TaskList tasks={tasks} />
    </div>
  )
}
```

### Form Handling with Validation

```tsx
'use client'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { taskSchema } from '@/lib/validation'

export function TaskForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(taskSchema)
  })

  const onSubmit = async (data) => {
    await api.createTask(data)
  }

  return <form onSubmit={handleSubmit(onSubmit)}>...</form>
}
```

### Error Handling

```tsx
'use client'
import { useState } from 'react'

export function TaskForm() {
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (data) => {
    try {
      setError(null)
      await api.createTask(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task')
    }
  }

  return (
    <>
      {error && <div className="text-red-500">{error}</div>}
      <form onSubmit={handleSubmit}>...</form>
    </>
  )
}
```

---

## 11. QUALITY CHECKLIST

Before submitting frontend code, verify:

- [ ] Component uses correct pattern (server vs client)
- [ ] All props properly typed with interfaces
- [ ] No 'any' types used
- [ ] Uses centralized API client (@/lib/api)
- [ ] Tailwind CSS utilities only (no inline styles)
- [ ] Responsive design implemented
- [ ] Form validation with Zod schemas
- [ ] Error handling implemented
- [ ] Loading states handled
- [ ] Accessibility considerations (ARIA labels, semantic HTML)
- [ ] Component follows existing patterns
- [ ] Tests written and passing

---

## 12. QUICK REFERENCE

### Import Paths

```typescript
// Components
import { Button } from '@/components/ui/Button'
import { TaskList } from '@/components/features/tasks/TaskList'

// Lib
import { api } from '@/lib/api'
import { Task } from '@/lib/types'
import { taskSchema } from '@/lib/validation'

// Next.js
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { redirect } from 'next/navigation'
```

### Common Commands

```bash
# Development
npm run dev              # Start dev server (localhost:3000)

# Building
npm run build            # Build for production
npm start                # Start production server

# Testing
npm test                 # Run tests
npm run test:watch       # Watch mode

# Linting
npm run lint             # Lint code
npm run lint:fix         # Fix linting issues

# Type checking
npm run type-check       # Check TypeScript types
```

---

## 13. PHASE III: CHATKIT INTEGRATION

### Overview

Phase III adds an AI-powered chatbot using OpenAI ChatKit for the chat interface. The chatbot allows users to manage tasks through natural language conversations.

### Installation

```bash
# Install OpenAI ChatKit
npm install @openai/chatkit

# ChatKit requires React 18+
npm install react@^18.0.0 react-dom@^18.0.0
```

### Usage in Chat Page

ChatKit components are used in the `/app/chat/page.tsx` file as a **client component** (requires `'use client'` directive).

```tsx
// app/chat/page.tsx
'use client'

import { ChatKit } from '@openai/chatkit'
import { useState } from 'react'

export default function ChatPage() {
  const [conversationId, setConversationId] = useState<number | null>(null)

  return (
    <div className="h-screen">
      <ChatKit
        apiEndpoint="/api/chat/message"
        conversationId={conversationId}
        onConversationChange={setConversationId}
      />
    </div>
  )
}
```

### Integration with Backend

ChatKit automatically:
- Sends user messages to the backend chat endpoint
- Displays AI responses in real-time
- Manages conversation history
- Handles loading states during AI processing
- Includes JWT cookies automatically (credentials: 'include')

---

## 14. CHAT PAGE STRUCTURE

### File Location

```
app/
└── chat/
    └── page.tsx  # AI chat interface
```

### Component Responsibilities

The chat page (`app/chat/page.tsx`) is responsible for:

1. **Rendering OpenAI ChatKit Component**
   - Import and display ChatKit from @openai/chatkit
   - Configure with backend endpoint

2. **Sending Messages to Backend**
   - Messages automatically sent to POST /api/chat/message
   - Includes conversation_id in requests

3. **Tracking Conversation State**
   - Store conversation_id in component state
   - Pass to ChatKit for conversation continuity

4. **Handling Loading States**
   - Show loading indicator while waiting for AI response
   - ChatKit handles this automatically

5. **Authentication (JWT Cookies)**
   - Reuses existing JWT authentication from Phase II
   - Cookies sent automatically with fetch credentials: 'include'

6. **Displaying Chat History**
   - ChatKit fetches and displays conversation history
   - Automatically scrolls to latest message

### Example Implementation

```tsx
// app/chat/page.tsx
'use client'

import { ChatKit } from '@openai/chatkit'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'

export default function ChatPage() {
  const router = useRouter()
  const { isAuthenticated, isLoading } = useAuth()
  const [conversationId, setConversationId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Redirect if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, isLoading, router])

  // Handle chat errors
  const handleError = (err: Error) => {
    if (err.message.includes('401')) {
      // Unauthorized - redirect to login
      router.push('/login')
    } else {
      setError('Failed to send message. Please try again.')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p>Loading...</p>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null // Will redirect
  }

  return (
    <div className="h-screen flex flex-col">
      <div className="bg-white shadow px-4 py-3">
        <h1 className="text-xl font-semibold">AI Task Assistant</h1>
        <p className="text-sm text-gray-600">
          Ask me to create, update, or manage your tasks
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <div className="flex-1 overflow-hidden">
        <ChatKit
          apiEndpoint="/api/chat/message"
          conversationId={conversationId}
          onConversationChange={setConversationId}
          onError={handleError}
          placeholder="Type a message... (e.g., 'Create a task to buy groceries')"
        />
      </div>
    </div>
  )
}
```

---

## 15. CHAT API INTEGRATION

### Backend Endpoint

**Endpoint:** `POST /api/chat/message`

**Note:** The actual backend endpoint URL is `http://localhost:8000/api/chat/message` (FastAPI backend). The frontend API client should route `/api/chat/message` to this backend URL.

### Request Format

```typescript
interface ChatMessageRequest {
  conversation_id?: number  // Optional for first message
  message: string           // User's message content
}
```

**Example Request:**
```json
{
  "conversation_id": 123,
  "message": "Create a high priority task for client presentation"
}
```

### Response Format

```typescript
interface ChatMessageResponse {
  conversation_id: number   // ID of the conversation
  response: string          // AI assistant's response
  tool_calls?: Array<{      // Optional: tools called by AI
    tool: string            // Tool name (e.g., "add_task")
    result: any             // Tool execution result
  }>
}
```

**Example Response:**
```json
{
  "conversation_id": 123,
  "response": "I've created a high priority task titled 'Client presentation'. Is there anything else you'd like to add?",
  "tool_calls": [
    {
      "tool": "add_task",
      "result": {
        "id": 456,
        "title": "Client presentation",
        "priority": "high"
      }
    }
  ]
}
```

### Integration Pattern

#### 1. Using Centralized API Client

Add chat methods to the API client:

```typescript
// lib/api.ts
class ApiClient {
  // ... existing methods ...

  // Chat API
  async sendChatMessage(
    message: string,
    conversationId?: number
  ): Promise<ChatMessageResponse> {
    return this.request<ChatMessageResponse>('/api/chat/message', {
      method: 'POST',
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    })
  }

  async getChatHistory(conversationId: number): Promise<Message[]> {
    return this.request<Message[]>(`/api/chat/conversations/${conversationId}/messages`)
  }

  async listConversations(): Promise<Conversation[]> {
    return this.request<Conversation[]>('/api/chat/conversations')
  }
}

// Types
export interface ChatMessageResponse {
  conversation_id: number
  response: string
  tool_calls?: Array<{
    tool: string
    result: any
  }>
}

export interface Message {
  id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at: string
}

export interface Conversation {
  id: number
  title: string
  created_at: string
  updated_at: string
  is_active: boolean
}
```

#### 2. Automatic Authentication

The API client automatically includes JWT cookies with every request:

```typescript
private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${this.baseUrl}${endpoint}`

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include', // ✅ Sends JWT cookie automatically
  })

  if (response.status === 401) {
    // Unauthorized - redirect to login
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  // ... rest of error handling
}
```

#### 3. Tracking Conversation State

```tsx
'use client'
import { useState } from 'react'
import { api } from '@/lib/api'

export function ChatInterface() {
  const [conversationId, setConversationId] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)

  const sendMessage = async (message: string) => {
    try {
      setLoading(true)
      const response = await api.sendChatMessage(message, conversationId)

      // Update conversation ID if this was the first message
      if (!conversationId) {
        setConversationId(response.conversation_id)
      }

      return response
    } catch (error) {
      console.error('Failed to send message:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      {loading && <div>Loading...</div>}
      {/* Chat UI */}
    </div>
  )
}
```

#### 4. Error Handling

```tsx
const sendMessage = async (message: string) => {
  try {
    const response = await api.sendChatMessage(message, conversationId)
    return response
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('401') || error.message === 'Unauthorized') {
        // Redirect to login (handled by API client)
        return
      } else if (error.message.includes('500')) {
        // Server error
        setError('AI service is currently unavailable. Please try again later.')
      } else {
        // Other errors
        setError('Failed to send message. Please try again.')
      }
    }
  }
}
```

---

## 16. CHATKIT CONFIGURATION

### Environment Variables

ChatKit requires the following environment variable:

```bash
# .env.local
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your_domain_key_here
```

### OpenAI Platform Setup

1. **Create Domain Key:**
   - Go to OpenAI Platform (https://platform.openai.com)
   - Navigate to API Keys section
   - Create a new domain-restricted key for your frontend domain
   - Add `localhost:3000` (development) and your production domain

2. **Domain Allowlist:**
   - ChatKit requires domain verification
   - Add allowed domains in OpenAI dashboard
   - Development: `http://localhost:3000`
   - Production: `https://yourdomain.com`

### ChatKit Component Configuration

```tsx
import { ChatKit } from '@openai/chatkit'

<ChatKit
  // Required: Backend chat endpoint
  apiEndpoint="/api/chat/message"

  // Optional: Conversation ID for continuity
  conversationId={conversationId}

  // Optional: Callback when conversation ID changes
  onConversationChange={(id) => setConversationId(id)}

  // Optional: Error handler
  onError={(error) => console.error('Chat error:', error)}

  // Optional: Placeholder text
  placeholder="Ask me anything about your tasks..."

  // Optional: Theme customization
  theme={{
    primaryColor: '#3B82F6',
    backgroundColor: '#FFFFFF',
    fontFamily: 'Inter, sans-serif',
  }}

  // Optional: Additional headers
  headers={{
    'X-Custom-Header': 'value',
  }}
/>
```

### Styling ChatKit

ChatKit uses its own internal styles, but you can customize with CSS:

```tsx
// Wrapper div with custom height
<div className="h-[calc(100vh-64px)]">
  <ChatKit apiEndpoint="/api/chat/message" />
</div>
```

```css
/* globals.css */
/* Override ChatKit styles if needed */
.chatkit-container {
  --chatkit-primary: #3B82F6;
  --chatkit-background: #FFFFFF;
  --chatkit-text: #111827;
}
```

---

## 17. CHAT NAVIGATION

### Adding Chat Link to Header

Update the Header component to include a "Chat" navigation item when the user is logged in:

```tsx
// components/layout/Header.tsx
'use client'

import Link from 'next/link'
import { useAuth } from '@/lib/auth'
import { Button } from '@/components/ui/Button'
import { api } from '@/lib/api'

export function Header() {
  const { user, isAuthenticated } = useAuth()

  const handleLogout = async () => {
    await api.logout()
    window.location.href = '/login'
  }

  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-gray-900">
            Todo App
          </Link>

          <nav className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                <Link href="/tasks" className="text-gray-700 hover:text-gray-900">
                  Tasks
                </Link>
                {/* Phase III: Chat navigation */}
                <Link href="/chat" className="text-gray-700 hover:text-gray-900">
                  Chat
                </Link>
                <span className="text-gray-600">Hello, {user?.name}</span>
                <Button onClick={handleLogout} variant="outline">
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link href="/login">
                  <Button variant="outline">Login</Button>
                </Link>
                <Link href="/signup">
                  <Button>Sign Up</Button>
                </Link>
              </>
            )}
          </nav>
        </div>
      </div>
    </header>
  )
}
```

### Navigation Behavior

- **Chat link visible:** Only when user is authenticated
- **Chat route:** `/chat` (protected route)
- **Active state:** Use `usePathname()` to highlight active route

```tsx
'use client'
import { usePathname } from 'next/navigation'

export function Header() {
  const pathname = usePathname()

  return (
    <nav>
      <Link
        href="/tasks"
        className={pathname === '/tasks' ? 'text-blue-600 font-semibold' : 'text-gray-700'}
      >
        Tasks
      </Link>
      <Link
        href="/chat"
        className={pathname === '/chat' ? 'text-blue-600 font-semibold' : 'text-gray-700'}
      >
        Chat
      </Link>
    </nav>
  )
}
```

### Mobile Navigation

For mobile views, include chat in the mobile menu:

```tsx
<div className="md:hidden">
  <button onClick={() => setMenuOpen(!menuOpen)}>
    Menu
  </button>

  {menuOpen && (
    <div className="mt-2 space-y-2">
      <Link href="/tasks">Tasks</Link>
      <Link href="/chat">Chat</Link>
    </div>
  )}
</div>
```

---

## 18. COMPONENT GUIDELINES (PHASE III)

### ChatPage Component

**Location:** `app/chat/page.tsx`

**Pattern:** Client component (`'use client'`)

**Responsibilities:**
- Render OpenAI ChatKit component
- Manage conversation state (conversation_id)
- Handle authentication (redirect if not logged in)
- Display loading states
- Handle errors (401, 500, network errors)

**Example:**
```tsx
'use client'
import { ChatKit } from '@openai/chatkit'
import { useState } from 'react'

export default function ChatPage() {
  const [conversationId, setConversationId] = useState<number | null>(null)

  return (
    <div className="h-screen">
      <ChatKit
        apiEndpoint="/api/chat/message"
        conversationId={conversationId}
        onConversationChange={setConversationId}
      />
    </div>
  )
}
```

### Type Definitions for Chat

```typescript
// lib/types.ts

// Chat message types
export interface ChatMessage {
  id: number
  conversation_id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at: string
}

export interface Conversation {
  id: number
  user_id: number
  title: string
  created_at: string
  updated_at: string
  is_active: boolean
}

export interface ChatMessageRequest {
  conversation_id?: number
  message: string
}

export interface ChatMessageResponse {
  conversation_id: number
  response: string
  tool_calls?: Array<{
    tool: string
    result: any
  }>
}
```

---

## 19. PHASE III QUALITY CHECKLIST

Before submitting Phase III frontend code, verify:

**ChatKit Integration:**
- [ ] OpenAI ChatKit installed (`npm install @openai/chatkit`)
- [ ] NEXT_PUBLIC_OPENAI_DOMAIN_KEY environment variable set
- [ ] ChatKit component properly configured
- [ ] Chat page is a client component (`'use client'`)

**API Integration:**
- [ ] Chat methods added to centralized API client
- [ ] API calls use `credentials: 'include'` for JWT cookies
- [ ] 401 errors redirect to login page
- [ ] 500 errors show user-friendly message

**State Management:**
- [ ] conversation_id tracked in component state
- [ ] conversation_id passed to ChatKit
- [ ] conversation_id sent with API requests

**Authentication:**
- [ ] Chat page checks authentication status
- [ ] Redirects to login if not authenticated
- [ ] JWT cookie sent automatically with requests

**UI/UX:**
- [ ] Loading states displayed during AI processing
- [ ] Error messages user-friendly and actionable
- [ ] Chat UI responsive (mobile + desktop)
- [ ] Chat navigation link visible when logged in

**Types:**
- [ ] Chat types defined in lib/types.ts
- [ ] API methods properly typed
- [ ] Component props properly typed

---

**Project:** Phase II-III - Full-Stack Web Application with AI Chatbot
**Frontend Stack:** Next.js 16+ (App Router) + TypeScript + Tailwind CSS + OpenAI ChatKit
**Authentication:** Better Auth (JWT cookies)
**Last Updated:** 2026-01-12
**Status:** Phase III - AI Chatbot Development
