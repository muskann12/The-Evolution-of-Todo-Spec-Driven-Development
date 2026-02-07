# UI Specification: Layouts

**Document:** Layout Specifications
**Framework:** Next.js 16+ (App Router)
**Last Updated:** 2025-12-31

---

## Overview

Layout specifications for Next.js App Router layouts. Layouts wrap pages and provide shared UI elements.

---

## Layout Structure

```
app/
├── layout.tsx                    # Root layout (all pages)
│
├── (auth)/                       # Auth pages (no extra layout)
│   ├── login/page.tsx
│   └── signup/page.tsx
│
└── (dashboard)/                  # Protected pages
    ├── layout.tsx               # Dashboard layout
    └── tasks/page.tsx
```

---

## Layouts

### 1. Root Layout

**File:** `app/layout.tsx`
**Type:** Server component
**Applies to:** All pages

**Purpose:** Global layout with metadata and providers

**Structure:**
```tsx
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <title>Todo Manager</title>
        <meta name="description" content="..." />
      </head>
      <body>
        <QueryProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  )
}
```

**Features:**
- Global providers (React Query, Auth)
- Global styles
- Metadata

---

### 2. Dashboard Layout

**File:** `app/(dashboard)/layout.tsx`
**Type:** Server component
**Applies to:** All protected pages (`/tasks`, `/profile`)

**Purpose:** Shared layout for authenticated pages

**Structure:**
```tsx
export default function DashboardLayout({ children }) {
  return (
    <div>
      <Header />
      <main className="max-w-7xl mx-auto px-4 py-8">
        {children}
      </main>
      <Footer />
    </div>
  )
}
```

**Features:**
- Header with navigation
- Main content area
- Footer
- Sidebar (future)

---

## Layout Components

### Header

Location: Shown in dashboard layout

**Contents:**
- App logo/name
- Navigation links
- User menu
- Logout button

**Styling:**
- Fixed/sticky header
- White background
- Shadow

---

### Footer

Location: Shown in dashboard layout

**Contents:**
- Copyright notice
- Links (About, Privacy, Terms)

**Styling:**
- Gray background
- Small text
- Centered

---

## Responsive Design

### Mobile (< 768px)
- Stack navigation vertically
- Hide sidebar (if implemented)
- Full-width content

### Tablet (768px - 1024px)
- Horizontal navigation
- Show sidebar (if implemented)
- Constrained content width

### Desktop (> 1024px)
- Full layout with sidebar
- Wide content area
- Fixed header

---

## Related Specifications

- `@specs/ui/pages.md` - Page specifications
- `@specs/ui/components.md` - Component specifications
- `@frontend/CLAUDE.md` - Frontend implementation guide

---

**Document Type:** UI Layout Specification
**Status:** Ready for Implementation
**Priority:** P0 (Critical)
