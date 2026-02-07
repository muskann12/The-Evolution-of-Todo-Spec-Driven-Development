# Skill: Add React Component (Next.js)

## Description
Create reusable React components for the Next.js frontend with TypeScript, proper state management, and styling.

## When to Use
- Need a new UI component (button, card, form, modal, etc.)
- Creating reusable component library
- Building feature-specific components

## Prerequisites
- Next.js project set up
- TypeScript configured
- Component folder structure exists

## Workflow

### 1. Plan Component Structure
- What is the component's purpose?
- What props does it need?
- Does it need state?
- Will it interact with API?
- What events should it handle?

### 2. Create Component File
```typescript
// components/TodoItem.tsx
import { useState } from 'react';

interface TodoItemProps {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'High' | 'Medium' | 'Low';
  onToggle: (id: number) => void;
  onDelete: (id: number) => void;
}

export function TodoItem({
  id,
  title,
  description,
  completed,
  priority,
  onToggle,
  onDelete
}: TodoItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const priorityColors = {
    High: 'text-red-600',
    Medium: 'text-yellow-600',
    Low: 'text-blue-600'
  };

  return (
    <div className="border rounded-lg p-4 mb-2 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={completed}
            onChange={() => onToggle(id)}
            className="w-5 h-5"
          />
          <div>
            <h3 className={`font-semibold ${completed ? 'line-through text-gray-500' : ''}`}>
              {title}
            </h3>
            <span className={`text-sm ${priorityColors[priority]}`}>
              {priority} Priority
            </span>
          </div>
        </div>
        <div className="flex gap-2">
          {description && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-blue-500 hover:text-blue-700"
            >
              {isExpanded ? 'Hide' : 'Show'} Details
            </button>
          )}
          <button
            onClick={() => onDelete(id)}
            className="text-red-500 hover:text-red-700"
          >
            Delete
          </button>
        </div>
      </div>
      {isExpanded && description && (
        <p className="mt-2 text-gray-600">{description}</p>
      )}
    </div>
  );
}
```

### 3. Create Component Tests
```typescript
// __tests__/TodoItem.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { TodoItem } from '@/components/TodoItem';

describe('TodoItem', () => {
  const mockTodo = {
    id: 1,
    title: 'Test Todo',
    description: 'Test Description',
    completed: false,
    priority: 'High' as const
  };

  it('renders todo item correctly', () => {
    render(
      <TodoItem
        {...mockTodo}
        onToggle={jest.fn()}
        onDelete={jest.fn()}
      />
    );

    expect(screen.getByText('Test Todo')).toBeInTheDocument();
    expect(screen.getByText('High Priority')).toBeInTheDocument();
  });

  it('calls onToggle when checkbox is clicked', () => {
    const handleToggle = jest.fn();
    render(
      <TodoItem {...mockTodo} onToggle={handleToggle} onDelete={jest.fn()} />
    );

    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);

    expect(handleToggle).toHaveBeenCalledWith(1);
  });

  it('calls onDelete when delete button is clicked', () => {
    const handleDelete = jest.fn();
    render(
      <TodoItem {...mockTodo} onToggle={jest.fn()} onDelete={handleDelete} />
    );

    const deleteButton = screen.getByText('Delete');
    fireEvent.click(deleteButton);

    expect(handleDelete).toHaveBeenCalledWith(1);
  });
});
```

### 4. Add to Component Index
```typescript
// components/index.ts
export { TodoItem } from './TodoItem';
export { TodoList } from './TodoList';
export { TodoForm } from './TodoForm';
```

### 5. Use Component in Page
```typescript
// app/page.tsx
import { TodoItem } from '@/components/TodoItem';

export default function HomePage() {
  const handleToggle = (id: number) => {
    // Handle toggle logic
  };

  const handleDelete = (id: number) => {
    // Handle delete logic
  };

  return (
    <div className="container mx-auto p-4">
      <TodoItem
        id={1}
        title="Sample Todo"
        completed={false}
        priority="High"
        onToggle={handleToggle}
        onDelete={handleDelete}
      />
    </div>
  );
}
```

## Checklist
- [ ] Component interface/props defined with TypeScript
- [ ] Component implements required functionality
- [ ] Event handlers properly typed
- [ ] Styling applied (Tailwind CSS)
- [ ] Accessibility attributes added (aria-label, role, etc.)
- [ ] Component is responsive
- [ ] Unit tests written
- [ ] Component documented
- [ ] Exported from components/index.ts
- [ ] Used in appropriate page/component

## Common Patterns

### Form Component
```typescript
// components/TodoForm.tsx
import { useState, FormEvent } from 'react';

interface TodoFormProps {
  onSubmit: (data: { title: string; description: string }) => void;
}

export function TodoForm({ onSubmit }: TodoFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    onSubmit({ title, description });
    setTitle('');
    setDescription('');
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Todo title"
        required
        className="w-full px-4 py-2 border rounded"
      />
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description (optional)"
        className="w-full px-4 py-2 border rounded"
      />
      <button
        type="submit"
        className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Add Todo
      </button>
    </form>
  );
}
```

### Client Component with State
```typescript
'use client';

import { useState, useEffect } from 'react';

export function TodoList() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTodos();
  }, []);

  const fetchTodos = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/todos');
      const data = await response.json();
      setTodos(data);
    } catch (error) {
      console.error('Failed to fetch todos:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {todos.map(todo => (
        <TodoItem key={todo.id} {...todo} />
      ))}
    </div>
  );
}
```

## Related Skills
- `web.add-page.md` - Use component in Next.js pages
- `web.integrate-api.md` - Connect component to API
- `web.setup-frontend.md` - Initial Next.js setup

## References
- [React Documentation](https://react.dev/)
- [Next.js Components](https://nextjs.org/docs/app/building-your-application/routing/pages-and-layouts)
- [TypeScript with React](https://react.dev/learn/typescript)
- [Tailwind CSS](https://tailwindcss.com/docs)
