# Skill: Setup Next.js Frontend

## Description
Initialize Next.js 14+ frontend with TypeScript, Tailwind CSS, and project structure.

## When to Use
- Starting Phase 2 frontend development
- Initial Next.js setup

## Workflow

### 1. Create Next.js App
```bash
cd phase-2-web-app
npx create-next-app@latest frontend --typescript --tailwind --app --eslint
cd frontend
```

### 2. Project Structure
```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── api/          # Optional API routes
├── components/
│   ├── TodoItem.tsx
│   └── TodoList.tsx
├── lib/
│   └── api.ts        # API client
├── types/
│   └── todo.ts       # TypeScript types
└── public/
```

### 3. Configure API Client
```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  async getTodos() {
    const res = await fetch(`${API_URL}/api/todos`);
    return res.json();
  },

  async createTodo(data: { title: string; description?: string }) {
    const res = await fetch(`${API_URL}/api/todos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return res.json();
  },
};
```

### 4. Environment Variables
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 5. Run Development Server
```bash
npm run dev
# Access at http://localhost:3000
```

## Checklist
- [ ] Next.js app created with TypeScript
- [ ] Tailwind CSS configured
- [ ] Project structure established
- [ ] API client created
- [ ] Environment variables set
- [ ] Development server runs

## References
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/)
