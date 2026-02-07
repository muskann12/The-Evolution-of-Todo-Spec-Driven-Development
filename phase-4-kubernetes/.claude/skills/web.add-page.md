# Skill: Add Next.js Page/Route

## Description
Create new pages and routes in Next.js using the App Router with TypeScript.

## When to Use
- Adding new pages to the application
- Creating dynamic routes
- Setting up layouts

## Workflow

### 1. Create Page File
```typescript
// app/todos/page.tsx
export default function TodosPage() {
  return (
    <div>
      <h1>Todos</h1>
    </div>
  );
}
```

### 2. Add Metadata
```typescript
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Todos | TODO App',
  description: 'Manage your todos',
};
```

### 3. Dynamic Routes
```typescript
// app/todos/[id]/page.tsx
interface PageProps {
  params: { id: string };
}

export default function TodoDetailPage({ params }: PageProps) {
  return <div>Todo ID: {params.id}</div>;
}
```

## Checklist
- [ ] Page file created in app directory
- [ ] Metadata defined
- [ ] TypeScript types added
- [ ] Layout applied
- [ ] Navigation links updated

## References
- [Next.js App Router](https://nextjs.org/docs/app)
- [Next.js Routing](https://nextjs.org/docs/app/building-your-application/routing)
