# Skill: Integrate Frontend with API

## Description
Connect Next.js frontend components to FastAPI backend endpoints.

## When to Use
- Fetching data from API
- Submitting forms to API
- Real-time updates

## Workflow

### 1. Create API Client
```typescript
// lib/api/todos.ts
export interface Todo {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'High' | 'Medium' | 'Low';
}

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export const todosApi = {
  async getAll(): Promise<Todo[]> {
    const res = await fetch(`${API_URL}/api/todos`);
    if (!res.ok) throw new Error('Failed to fetch todos');
    return res.json();
  },

  async create(data: Omit<Todo, 'id' | 'completed'>): Promise<Todo> {
    const res = await fetch(`${API_URL}/api/todos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create todo');
    return res.json();
  },

  async update(id: number, data: Partial<Todo>): Promise<Todo> {
    const res = await fetch(`${API_URL}/api/todos/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update todo');
    return res.json();
  },

  async delete(id: number): Promise<void> {
    const res = await fetch(`${API_URL}/api/todos/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete todo');
  },
};
```

### 2. Use in Component
```typescript
'use client';

import { useState, useEffect } from 'react';
import { todosApi, Todo } from '@/lib/api/todos';

export function TodoList() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTodos();
  }, []);

  const loadTodos = async () => {
    try {
      setLoading(true);
      const data = await todosApi.getAll();
      setTodos(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load todos');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (data: Omit<Todo, 'id' | 'completed'>) => {
    try {
      const newTodo = await todosApi.create(data);
      setTodos([...todos, newTodo]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create todo');
    }
  };

  const handleToggle = async (id: number) => {
    const todo = todos.find(t => t.id === id);
    if (!todo) return;

    try {
      const updated = await todosApi.update(id, { completed: !todo.completed });
      setTodos(todos.map(t => t.id === id ? updated : t));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update todo');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await todosApi.delete(id);
      setTodos(todos.filter(t => t.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete todo');
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-500">Error: {error}</div>;

  return (
    <div>
      {todos.map(todo => (
        <TodoItem
          key={todo.id}
          {...todo}
          onToggle={handleToggle}
          onDelete={handleDelete}
        />
      ))}
    </div>
  );
}
```

## Checklist
- [ ] API client created with typed functions
- [ ] Error handling implemented
- [ ] Loading states managed
- [ ] CORS configured in backend
- [ ] Environment variables set
- [ ] API calls tested

## References
- [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [React Query](https://tanstack.com/query) (optional)
