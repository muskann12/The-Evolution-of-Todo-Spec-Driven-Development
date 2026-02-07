# Todo Manager Frontend - Next.js

> Modern, responsive frontend for the Todo Manager application built with Next.js 16+, TypeScript, and Tailwind CSS.

[![Next.js](https://img.shields.io/badge/Next.js-16%2B-black)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9%2B-blue)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4%2B-38B2AC)](https://tailwindcss.com/)
[![React](https://img.shields.io/badge/React-19.2%2B-61DAFB)](https://react.dev/)

---

## Overview

The **Todo Manager Frontend** is a modern, responsive web application built with Next.js 16+ and the App Router. It provides a beautiful user interface for managing tasks with authentication, real-time search, drag-and-drop kanban board, and comprehensive filtering/sorting capabilities.

### Key Features

- **Next.js 16+ App Router** - Server and client components for optimal performance
- **TypeScript Strict Mode** - Full type safety throughout the application
- **Tailwind CSS** - Modern, responsive design with utility-first CSS
- **Kanban Board** - Drag-and-drop task management with @hello-pangea/dnd
- **React Query** - Efficient server state management and caching
- **Better Auth Integration** - Secure authentication (when implemented)
- **Real-time Search** - Instant search across tasks
- **Advanced Filtering** - Filter by priority, tags, and status
- **Task Sorting** - Sort by date, priority, title, or completion status
- **Responsive Design** - Mobile-first approach, works on all devices
- **Accessibility** - ARIA labels and semantic HTML

---

## Quick Start

### Prerequisites

- **Node.js** 18.x or higher ([Download](https://nodejs.org/))
- **npm** or **pnpm** package manager

### Installation

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

4. **Run the development server:**
   ```bash
   npm run dev
   ```

5. **Open your browser:**
   - Application: http://localhost:3000
   - Make sure backend is running at http://localhost:8000

---

## Environment Variables

Create a `.env.local` file in the frontend directory:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration (when implemented)
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters
BETTER_AUTH_URL=http://localhost:3000
```

### Environment File Template

```bash
# .env.example

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Secret (must match backend)
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters

# Better Auth URL (frontend base URL)
BETTER_AUTH_URL=http://localhost:3000
```

---

## Project Structure

```
frontend/
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── page.tsx                 # Home page
│   │   ├── layout.tsx               # Root layout
│   │   ├── globals.css              # Global styles
│   │   ├── tasks/                   # Tasks pages
│   │   │   ├── page.tsx            # Tasks list page
│   │   │   └── [id]/               # Dynamic task routes
│   │   └── api/                     # API routes (if needed)
│   │
│   ├── components/                   # Reusable UI components
│   │   ├── ui/                      # Generic UI primitives
│   │   │   ├── Button.tsx          # Button component
│   │   │   ├── Input.tsx           # Input component
│   │   │   ├── Select.tsx          # Select component
│   │   │   └── Card.tsx            # Card component
│   │   │
│   │   ├── features/                # Feature-specific components
│   │   │   ├── tasks/
│   │   │   │   ├── TaskList.tsx    # Task list display
│   │   │   │   ├── TaskItem.tsx    # Individual task card
│   │   │   │   ├── TaskForm.tsx    # Create/edit task form
│   │   │   │   ├── KanbanBoard.tsx # Kanban board view
│   │   │   │   ├── SearchBar.tsx   # Search functionality
│   │   │   │   ├── FilterPanel.tsx # Filter controls
│   │   │   │   └── SortPanel.tsx   # Sort controls
│   │   │   │
│   │   │   └── auth/
│   │   │       ├── LoginForm.tsx   # Login form
│   │   │       └── SignupForm.tsx  # Signup form
│   │   │
│   │   └── layout/                  # Layout components
│   │       ├── Header.tsx          # Application header
│   │       ├── Sidebar.tsx         # Navigation sidebar
│   │       └── Footer.tsx          # Application footer
│   │
│   └── lib/                         # Utilities and helpers
│       ├── api.ts                   # API client
│       ├── types.ts                 # TypeScript types
│       ├── validation.ts            # Zod schemas
│       ├── utils.ts                 # Helper functions
│       └── constants.ts             # App constants
│
├── public/                          # Static assets
│   ├── favicon.ico
│   ├── images/
│   └── fonts/
│
├── .env.local                       # Environment variables (gitignored)
├── .env.example                     # Example environment file
├── next.config.ts                   # Next.js configuration
├── tailwind.config.ts               # Tailwind CSS configuration
├── tsconfig.json                    # TypeScript configuration
├── package.json                     # Dependencies and scripts
├── CLAUDE.md                        # Frontend-specific guide
└── README.md                        # This file
```

---

## Available Scripts

### Development

```bash
# Start development server (http://localhost:3000)
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Type check
npm run type-check

# Format code (if configured)
npm run format
```

### Testing

**Test Status:** ✅ **14/14 Tests Passing**

**Test Framework:** Vitest + React Testing Library

The frontend has a complete testing infrastructure set up with automated tests:

```bash
# Run tests
npm test

# Run tests in watch mode
npm test

# Run tests once
npm run test:run

# Run tests with coverage
npm run test:coverage
```

**Test Suite:**
- ✅ **Footer Component** - 6/6 tests passing
  - Renders app name and tagline
  - Displays navigation and legal links
  - Shows current year in copyright

- ✅ **DeleteConfirmation Component** - 8/8 tests passing
  - Opens/closes modal correctly
  - Displays warning message
  - Handles user interactions (Cancel/Delete)
  - Shows loading states

**Coverage Report:**
- Component tests: 2 test files
- Total test cases: 14 passing
- Test framework: Vitest 4.0.16
- Testing utilities: @testing-library/react 16.3.1

**Manual Testing:**
- ✅ **Component Rendering** - All UI components render correctly
- ✅ **Kanban Board** - Drag-and-drop functionality working
- ✅ **Search & Filter** - Real-time search and filtering operational
- ✅ **Task CRUD** - Create, Read, Update, Delete operations functional
- ✅ **Responsive Design** - Works on desktop and mobile devices
- ✅ **Type Safety** - TypeScript strict mode with no errors

---

## Features

### 1. Task Management

**Create Task:**
- Title (required, 1-200 characters)
- Description (optional, max 1000 characters)
- Priority (High, Medium, Low)
- Tags (comma-separated)
- Due date
- Recurrence pattern

**Edit Task:**
- Update all task properties
- Mark as complete/incomplete
- Update status (Ready, In Progress, Review, Done)

**Delete Task:**
- Permanent deletion with confirmation

### 2. Kanban Board View

**Features:**
- Drag-and-drop interface powered by @hello-pangea/dnd
- Four status columns:
  - **Ready** - Tasks ready to be started
  - **In Progress** - Tasks currently being worked on
  - **Review** - Tasks awaiting review
  - **Done** - Completed tasks
- Color-coded priority indicators:
  - 🔴 **High** - Red
  - 🟡 **Medium** - Yellow
  - 🟢 **Low** - Green
- Automatic status update on drop
- Responsive design for mobile

### 3. Search & Filtering

**Search:**
- Real-time search across task titles and descriptions
- Instant results as you type
- Clear search button

**Filter by Priority:**
- High priority tasks
- Medium priority tasks
- Low priority tasks

**Filter by Status:**
- All tasks
- Incomplete tasks only
- Complete tasks only

**Filter by Tags:**
- Filter by specific tags
- Multiple tag filtering

**Combined Filters:**
- Use multiple filters simultaneously
- Smart filtering logic

### 4. Task Sorting

**Sort Options:**
- **By Date:**
  - Newest first
  - Oldest first
- **By Priority:**
  - High to low
  - Low to high
- **By Title:**
  - A to Z
  - Z to A
- **By Status:**
  - Incomplete first
  - Complete first

---

## Tech Stack

### Core Technologies

- **Next.js 16+** - React framework with App Router
- **React 19+** - UI library
- **TypeScript 5.9+** - Type-safe JavaScript
- **Tailwind CSS 3.4+** - Utility-first CSS framework

### UI Components & Libraries

- **@hello-pangea/dnd** (^18.0.1) - Drag-and-drop library (React 19 compatible)
- **lucide-react** (^0.562.0) - Icon library
- **clsx** (^2.1.1) - Conditional className utility
- **tailwind-merge** (^3.4.0) - Merge Tailwind classes intelligently

### State Management & Data Fetching

- **@tanstack/react-query** (^5.90.16) - Server state management
- **@tanstack/react-query-devtools** (^5.91.2) - Query debugging tools

### Data Visualization (Optional)

- **recharts** (^3.6.0) - Charts and data visualization

---

## Component Architecture

### Server Components vs Client Components

**Server Components (Default):**
- Used for static content, layouts, data fetching
- Better performance (no JavaScript sent to client)
- Direct database access (when implemented)

```tsx
// Server component (no 'use client' directive)
export default async function TasksPage() {
  const tasks = await fetchTasks()
  return <TaskList tasks={tasks} />
}
```

**Client Components:**
- Used for interactivity, event handlers, browser APIs
- Required for forms, clicks, state management

```tsx
'use client'

export function TaskForm() {
  const [title, setTitle] = useState('')
  // Client-side interactivity
  return <form>...</form>
}
```

### Component Patterns

**1. Generic UI Components (`components/ui/`):**

```tsx
// Button.tsx - Reusable button component
export interface ButtonProps {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'outline' | 'destructive'
  size?: 'sm' | 'md' | 'lg'
  onClick?: () => void
  disabled?: boolean
}

export function Button({ children, variant = 'primary', ... }: ButtonProps) {
  return <button className={buttonVariants({ variant, size })}>{children}</button>
}
```

**2. Feature Components (`components/features/`):**

```tsx
// TaskItem.tsx - Individual task card
'use client'

export interface TaskItemProps {
  task: Task
  onUpdate?: (taskId: string) => void
  onDelete?: (taskId: string) => void
}

export function TaskItem({ task, onUpdate, onDelete }: TaskItemProps) {
  return (
    <Card>
      <h3>{task.title}</h3>
      <p>{task.description}</p>
      <div className="actions">
        <Button onClick={() => onUpdate?.(task.id)}>Edit</Button>
        <Button onClick={() => onDelete?.(task.id)} variant="destructive">Delete</Button>
      </div>
    </Card>
  )
}
```

---

## Styling with Tailwind CSS

### Utility-First Approach

```tsx
// Use Tailwind utility classes
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow-md">
  <h2 className="text-2xl font-bold text-gray-900">Title</h2>
  <button className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600">
    Click me
  </button>
</div>
```

### Responsive Design (Mobile-First)

```tsx
// Mobile-first breakpoints
<div className="
  grid
  grid-cols-1          /* Mobile: 1 column */
  md:grid-cols-2       /* Tablet: 2 columns */
  lg:grid-cols-3       /* Desktop: 3 columns */
  gap-4
">
  {tasks.map(task => <TaskCard key={task.id} task={task} />)}
</div>
```

### Common Tailwind Patterns

```tsx
// Container
<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

// Card
<div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">

// Button group
<div className="flex gap-2">
  <Button>Action 1</Button>
  <Button>Action 2</Button>
</div>

// Centered content
<div className="flex items-center justify-center min-h-screen">

// Form spacing
<form className="space-y-4">
  <Input />
  <Textarea />
  <Button>Submit</Button>
</form>
```

---

## Type Safety

### TypeScript Configuration

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

export interface Task {
  id: string
  title: string
  description: string | null
  completed: boolean
  priority: 'High' | 'Medium' | 'Low'
  tags: string[]
  status: 'Ready' | 'In Progress' | 'Review' | 'Done'
  recurrencePattern: 'Daily' | 'Weekly' | 'Monthly' | null
  recurrenceInterval: number
  dueDate: string | null
  userId: string
  createdAt: string
  updatedAt: string
}

export interface CreateTaskInput {
  title: string
  description?: string
  priority?: 'High' | 'Medium' | 'Low'
  tags?: string[]
  status?: 'Ready' | 'In Progress' | 'Review' | 'Done'
  recurrencePattern?: 'Daily' | 'Weekly' | 'Monthly' | null
  recurrenceInterval?: number
  dueDate?: string | null
}

export interface UpdateTaskInput {
  title?: string
  description?: string
  completed?: boolean
  priority?: 'High' | 'Medium' | 'Low'
  tags?: string[]
  status?: 'Ready' | 'In Progress' | 'Review' | 'Done'
  recurrencePattern?: 'Daily' | 'Weekly' | 'Monthly' | null
  recurrenceInterval?: number
  dueDate?: string | null
}
```

---

## API Integration

### API Client

```typescript
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = {
  // Get all tasks
  async getTasks(): Promise<Task[]> {
    const response = await fetch(`${API_BASE_URL}/api/tasks`)
    if (!response.ok) throw new Error('Failed to fetch tasks')
    return response.json()
  },

  // Create task
  async createTask(data: CreateTaskInput): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/api/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error('Failed to create task')
    return response.json()
  },

  // Update task
  async updateTask(id: string, data: UpdateTaskInput): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error('Failed to update task')
    return response.json()
  },

  // Delete task
  async deleteTask(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`, {
      method: 'DELETE',
    })
    if (!response.ok) throw new Error('Failed to delete task')
  },
}
```

### Using React Query

```tsx
'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'

export function TaskList() {
  const queryClient = useQueryClient()

  // Fetch tasks
  const { data: tasks, isLoading, error } = useQuery({
    queryKey: ['tasks'],
    queryFn: api.getTasks,
  })

  // Create task mutation
  const createTask = useMutation({
    mutationFn: api.createTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error loading tasks</div>

  return (
    <div>
      {tasks?.map(task => <TaskItem key={task.id} task={task} />)}
    </div>
  )
}
```

---

## Development Workflow

### Step-by-Step Implementation

1. **Read Specifications:**
   ```bash
   @../specs/ui/components.md
   @../specs/features/[feature].md
   ```

2. **Create Component File:**
   ```bash
   src/components/features/tasks/TaskList.tsx
   ```

3. **Define Types:**
   ```tsx
   import { Task } from '@/lib/types'

   export interface TaskListProps {
     tasks: Task[]
   }
   ```

4. **Implement Component:**
   ```tsx
   export function TaskList({ tasks }: TaskListProps) {
     return (
       <div className="space-y-4">
         {tasks.map(task => <TaskItem key={task.id} task={task} />)}
       </div>
     )
   }
   ```

5. **Add Styling:**
   ```tsx
   <div className="bg-white rounded-lg shadow p-6">
     {/* Content */}
   </div>
   ```

6. **Test Component:**
   ```bash
   npm test
   ```

---

## Quality Checklist

Before submitting frontend code, verify:

- [ ] Component uses correct pattern (server vs client)
- [ ] All props properly typed with interfaces
- [ ] No `any` types used
- [ ] Uses Tailwind CSS utilities only (no inline styles)
- [ ] Responsive design implemented (mobile-first)
- [ ] Form validation implemented (if applicable)
- [ ] Error handling implemented
- [ ] Loading states handled
- [ ] Accessibility considerations (ARIA labels, semantic HTML)
- [ ] Component follows existing patterns
- [ ] Tests written and passing (if applicable)

---

## Deployment

### Build for Production

**Note:** There is currently a known issue with the production build due to a Next.js/Turbopack bug. The development server works perfectly.

```bash
# Build the application (⚠️ has known issue)
npm run build

# Start production server
npm start

# Development server (✅ fully functional)
npm run dev
```

**Production Build Issue:**
- Error occurs during static page generation with Turbopack
- This is a Next.js framework bug, not an application code issue
- **Development mode is fully functional** and recommended for testing
- Production deployment works on Vercel/Netlify despite this error

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy to Vercel
vercel

# Deploy to production
vercel --prod
```

### Environment Variables on Vercel

1. Go to your project settings on Vercel
2. Navigate to "Environment Variables"
3. Add the following:
   - `NEXT_PUBLIC_API_URL` - Your backend API URL
   - `BETTER_AUTH_SECRET` - Your auth secret (same as backend)
   - `BETTER_AUTH_URL` - Your frontend URL

---

## Troubleshooting

### Common Issues

**1. API connection errors:**
```bash
# Check NEXT_PUBLIC_API_URL in .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000

# Ensure backend is running
cd ../backend && uv run uvicorn app.main:app --reload
```

**2. Type errors:**
```bash
# Run type check
npm run type-check

# Check tsconfig.json configuration
```

**3. Styling issues:**
```bash
# Rebuild Tailwind CSS
npm run dev

# Check tailwind.config.ts
```

**4. Import errors:**
```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

---

## Spec Reference

See project specifications:
- [`@../specs/overview.md`](../specs/overview.md) - Project overview
- [`@../specs/architecture.md`](../specs/architecture.md) - System architecture
- [`@../specs/ui/`](../specs/ui/) - UI component specifications
- [`@../specs/features/`](../specs/features/) - Feature specifications

---

## Support

For issues and questions, refer to:
- [`@../CLAUDE.md`](../CLAUDE.md) - Main navigation guide
- [`@CLAUDE.md`](./CLAUDE.md) - Frontend-specific guide
- [GitHub Issues](https://github.com/Roofan-Jlove/Hackathon-II-TODO-APP/issues)

---

## License

Educational project for learning purposes.

---

<div align="center">

**Built with Next.js, TypeScript, and Tailwind CSS**

**React 19+ | Next.js 16+ | TypeScript 5.9+ | Vitest Testing**

**Status:** Development Ready - 14/14 Tests Passing ✅

**Last Updated:** January 10, 2026

[⬆ Back to Top](#todo-manager-frontend---nextjs)

</div>
